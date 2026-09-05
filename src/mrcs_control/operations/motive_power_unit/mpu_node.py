"""
Created on 31 Aug 2026

@author: Bruno Beloff (bbeloff@me.com)

A service that manages motive power units

Test with:
mrcs_control_subscriber -v -s MPU.*.002
"""

from collections.abc import Callable
from typing import List

from mrcs_control.cli.inventory.mpu_inventory import MPUInventory
from mrcs_control.db.db_client import DbClient
from mrcs_control.dcc.z21.command.command import Command, XCommand
from mrcs_control.equipment.motive_power_unit.persistent_mpu_status import PersistentMPUStatus
from mrcs_control.messaging.mq_topology import MQTopology
from mrcs_control.operations.async_messaging_node import AsyncSubscriberNode
from mrcs_control.operations.control_router.control_router_identity import ControlRouterSerial
from mrcs_control.operations.control_router.control_router_node import ControlRouterNode
from mrcs_control.operations.motive_power_unit.mpu_node_identity import MPUNodeSerial
from mrcs_control.operations.node_topology import NodeTopology
from mrcs_core.data.equipment_identity import EquipmentFilter, EquipmentIdentifier, EquipmentType
from mrcs_core.data.json import JSONable
from mrcs_core.equipment.motive_power_unit.mpu_configuration_report import MPUConfigurationReport
from mrcs_core.equipment.motive_power_unit.mpu_decoder_report import MPUDecoderReport
from mrcs_core.equipment.motive_power_unit.mpu_status import MPUStatus
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import PublicationRoutingKey, SubscriptionRoutingKey


# --------------------------------------------------------------------------------------------------------------------

class MPUNode(AsyncSubscriberNode):
    """
    a service that manages motive power units
    """


    @classmethod
    def id(cls):
        return EquipmentIdentifier(EquipmentType.MPU, None, MPUNodeSerial.NODE)


    @classmethod
    def subscription_routing_keys(cls) -> list[SubscriptionRoutingKey]:
        subscriptions = [SubscriptionRoutingKey(EquipmentFilter.any(), cls.id())]

        for serial in [ControlRouterSerial.MPU]:
            subscriptions.append(
                SubscriptionRoutingKey(EquipmentFilter.construct(EquipmentType.CRT, None, serial),
                                       EquipmentFilter.any()))

        return subscriptions


    @classmethod
    def control_routing_key(cls):
        return PublicationRoutingKey(cls.id(), ControlRouterNode.id())


    @classmethod
    def status_routing_key(cls):
        source = EquipmentIdentifier(EquipmentType.MPU, None, MPUNodeSerial.MPU_STATUS)
        return PublicationRoutingKey(source, EquipmentFilter.any())


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: NodeTopology.ServiceConfiguration, on_message: Callable[JSONable] | None = None):
        super().__init__(ops, MQTopology.SINGLE_PROCESS)

        self.__on_message = on_message


    # ----------------------------------------------------------------------------------------------------------------

    def handle_startup(self):
        self.__publish_startup_messages()
        self.logger.info('ready')


    def handle_message(self, message: Message):
        self.logger.debug(f'handle_message:{message.routing_key}')

        try:
            if message.routing_key.target == self.id():
                self.logger.info(f'received command:{message.body}')
                # TODO: act on commands
                return

            body_type = message.body.get('type')

            if body_type == MPUConfigurationReport.__name__:
                report = MPUConfigurationReport.construct_from_jdict(message.body)
                status = PersistentMPUStatus.update_from_configuration_report(report)

                self.__publish_update_message(status)

            if body_type == MPUDecoderReport.__name__:
                report = MPUDecoderReport.construct_from_jdict(message.body)
                PersistentMPUStatus.update_from_decoder_report(report)

            if self.on_message:
                self.on_message(message)

        except Exception as exc:
            self.logger.warning(f'handle_message:{type(exc).__name__}:{exc} on:{message}')


    # ----------------------------------------------------------------------------------------------------------------

    def __publish_startup_messages(self):
        self.logger.debug('publish_startup_messages')

        for address in PersistentMPUStatus.find_addresses():
            message = Message(self.control_routing_key(), Command.lan_railcom_get_data(address))
            self.async_loop.create_task(self.publish(message))

            message = Message(self.control_routing_key(), XCommand.lan_x_get_mpu(address))
            self.async_loop.create_task(self.publish(message))


    def __publish_update_message(self, status: MPUStatus):
        self.logger.debug('publish_update_message')

        message = Message(self.status_routing_key(), status)
        self.async_loop.create_task(self.publish(message))


    # ----------------------------------------------------------------------------------------------------------------

    def populate(self, mpus: MPUInventory) -> None:
        DbClient.set_client_db_mode(self.ops.db_mode)
        PersistentMPUStatus.recreate_tables()

        for mpu in mpus.items:
            PersistentMPUStatus.narrow(mpu).save()


    def find_all_mpus(self) -> List[PersistentMPUStatus]:
        self.__setup()
        return PersistentMPUStatus.find_all()


    def run(self, *args, **kwargs) -> None:
        self.__setup()
        super().run()


    def __setup(self):
        DbClient.set_client_db_mode(self.ops.db_mode)
        PersistentMPUStatus.create_tables()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def on_message(self):
        return self.__on_message


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        on_message = self.on_message.__name__
        routing_keys = '[' + ', '.join([str(key) for key in self.subscription_routing_keys()]) + ']'

        return (f'MPUNode:{{routing_keys:{routing_keys}, on_message:{on_message}, '
                f'ops:{self.ops}, mq_client:{self.mq_client}}}')
