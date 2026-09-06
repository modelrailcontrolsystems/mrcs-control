"""
Created on 6 Sep 2026

@author: Bruno Beloff (bbeloff@me.com)

A service that monitors the aspect of each MPU

Test with:
mrcs_control_subscriber -v -s TEL.*.2
"""

from collections.abc import Callable
from typing import List

from mrcs_control.cli.inventory.block_inventory import BlockInventory
from mrcs_control.cli.inventory.turnout_inventory import TurnoutInventory
from mrcs_control.db.db_client import DbClient
from mrcs_control.equipment.block.persistent_block_status import PersistentBlockStatus
from mrcs_control.equipment.turnout.persistent_turnout_status import PersistentTurnoutStatus
from mrcs_control.messaging.mq_topology import MQTopology
from mrcs_control.operations.async_messaging_node import AsyncSubscriberNode
from mrcs_control.operations.motive_power_unit.mpu_node_identity import MPUNodeSerial
from mrcs_control.operations.node_topology import NodeTopology
from mrcs_control.operations.telemetry.telementry_node_identity import TelemetryNodeSerial
from mrcs_control.operations.track.track_node_identity import TrackNodeSerial
from mrcs_core.data.equipment_identity import EquipmentFilter, EquipmentIdentifier, EquipmentType
from mrcs_core.data.json import JSONable
from mrcs_core.equipment.block.block_status import BlockStatus
from mrcs_core.equipment.motive_power_unit.mpu_status import MPUStatus
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import PublicationRoutingKey, SubscriptionRoutingKey


# --------------------------------------------------------------------------------------------------------------------

class TelemetryNode(AsyncSubscriberNode):
    """
    a service that monitors the aspect of each MPU
    """


    @classmethod
    def id(cls):
        return EquipmentIdentifier(EquipmentType.TEL, None, TelemetryNodeSerial.NODE)


    @classmethod
    def subscription_routing_keys(cls) -> list[SubscriptionRoutingKey]:
        subscriptions = [SubscriptionRoutingKey(EquipmentFilter.any(), cls.id())]

        mpu_source = EquipmentFilter.construct(EquipmentType.MPU, None, MPUNodeSerial.MPU_STATUS)
        track_source = EquipmentFilter.construct(EquipmentType.TRK, None, TrackNodeSerial.BLOCK_STATUS)

        for source in [mpu_source, track_source]:
            subscriptions.append(SubscriptionRoutingKey(source, EquipmentFilter.any()))

        return subscriptions


    @classmethod
    def aspect_routing_key(cls):
        source = EquipmentIdentifier(EquipmentType.TEL, None, TelemetryNodeSerial.MPU_ASPECT)
        return PublicationRoutingKey(source, EquipmentFilter.any())


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: NodeTopology.ServiceConfiguration, on_message: Callable[JSONable] | None = None):
        super().__init__(ops, MQTopology.SINGLE_PROCESS)

        self.__on_message = on_message


    # ----------------------------------------------------------------------------------------------------------------

    def handle_startup(self):
        self.logger.info('ready')


    def handle_message(self, message: Message):
        self.logger.debug(f'handle_message:{message}')

        try:
            if message.routing_key.target == self.id():
                self.logger.info(f'received command:{message.body}')
                # TODO: act on commands
                return

            body_type = message.body.get('type')

            if body_type == BlockStatus.type_name():
                report = BlockStatus.construct_from_jdict(message.body)
                self.logger.debug(report)

            elif body_type == MPUStatus.type_name():
                report = MPUStatus.construct_from_jdict(message.body)
                self.logger.debug(report)

            else:
                self.logger.warning(f'upsupported message:{message}')

            if self.on_message:
                self.on_message(message)

        except Exception as exc:
            self.logger.warning(f'handle_message:{type(exc).__name__}:{exc} on:{message}')


    # ----------------------------------------------------------------------------------------------------------------

    def __publish_update_message(self, aspect: BlockStatus):
        self.logger.debug('publish_update_message')

        message = Message(self.aspect_routing_key(), aspect)
        self.async_loop.create_task(self.publish(message))


    # ----------------------------------------------------------------------------------------------------------------

    def populate(self, blocks: BlockInventory, turnouts: TurnoutInventory) -> None:
        DbClient.set_client_db_mode(self.ops.db_mode)
        # PersistentBlockStatus.recreate_tables()
        # PersistentTurnoutStatus.recreate_tables()

        for block in blocks.items:
            PersistentBlockStatus.narrow(block).save()

        for turnout in turnouts.items:
            PersistentTurnoutStatus.narrow(turnout).save()


    def find_all_blocks(self) -> List[PersistentBlockStatus]:
        self.__setup()
        return PersistentBlockStatus.find_all()


    def find_all_turnouts(self) -> List[PersistentTurnoutStatus]:
        self.__setup()
        return PersistentTurnoutStatus.find_all()


    def run(self, *args, **kwargs) -> None:
        self.__setup()
        super().run()


    def __setup(self):
        DbClient.set_client_db_mode(self.ops.db_mode)
        # PersistentBlockStatus.create_tables()
        # PersistentTurnoutStatus.create_tables()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def on_message(self):
        return self.__on_message


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        on_message = self.on_message.__name__
        routing_keys = '[' + ', '.join([str(key) for key in self.subscription_routing_keys()]) + ']'

        return (f'TelemetryNode:{{routing_keys:{routing_keys}, on_message:{on_message}, '
                f'ops:{self.ops}, mq_client:{self.mq_client}}}')
