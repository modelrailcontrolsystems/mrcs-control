"""
Created on 31 Oct 2026

@author: Bruno Beloff (bbeloff@me.com)

A service that runs MPU speed trials

Test with:
mrcs_control_subscriber -v -s SPD.*.2
"""

from collections.abc import Callable
from typing import List

from mrcs_control.db.db_client import DbClient
from mrcs_control.equipment.block.persistent_block_status import PersistentBlockStatus
from mrcs_control.messaging.mq_topology import MQTopology
from mrcs_control.operations.async_messaging_node import AsyncSubscriberNode
from mrcs_control.operations.motive_power_unit.mpu_node_identity import MPUNodeSerial
from mrcs_control.operations.speed.speed_node_identity import SpeedNodeSerial
from mrcs_control.operations.track.track_node_identity import TrackNodeSerial
from mrcs_core.data.json import JSONable, JSONify
from mrcs_core.equipment.equipment_enums import EquipmentType
from mrcs_core.equipment.equipment_identity import EquipmentFilter, EquipmentIdentifier
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import PublicationRoutingKey, SubscriptionRoutingKey
from mrcs_core.operations.node_topology import NodeTopology


# --------------------------------------------------------------------------------------------------------------------

class SpeedNode(AsyncSubscriberNode):
    """
    a service that runs MPU speed trials
    """


    @classmethod
    def id(cls):
        return EquipmentIdentifier(EquipmentType.SPD, None, SpeedNodeSerial.NODE)


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
        source = EquipmentIdentifier(EquipmentType.SPD, None, SpeedNodeSerial.SPEED_REPORT)
        return PublicationRoutingKey(source, EquipmentFilter.any())


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: NodeTopology.ServiceConfiguration, on_message: Callable[JSONable] | None = None):
        super().__init__(ops, MQTopology.SINGLE_PROCESS)

        self.__on_message = on_message
        self.__initial_publication: Message | None = None
        self.__final_publication: Message | None = None


    # ----------------------------------------------------------------------------------------------------------------

    def handle_startup(self):
        self.async_loop.create_task(self.publish_message(self.initial_publication))
        self.logger.info('ready')


    async def publish_message(self, message):
        self.logger.debug(f'publish_message:{message}')

        if message is not None:
            await self.publish(message)


    def handle_message(self, message: Message):
        self.logger.debug(f'handle_message: {JSONify.as_jdict(message)}')
        self.on_message(message)


    # ----------------------------------------------------------------------------------------------------------------

    def find_all_blocks(self) -> List[PersistentBlockStatus]:
        self.__setup()
        return PersistentBlockStatus.find_all()


    def __setup(self):
        DbClient.set_client_db_mode(self.ops.db_mode)


    # ----------------------------------------------------------------------------------------------------------------

    def run(self, initial_publication=None, final_publication=None, *args, **kwargs) -> None:
        self.__initial_publication = initial_publication
        self.__final_publication = final_publication
        self.__setup()

        super().run(*args, **kwargs)


    async def halt(self):
        self.logger.debug('SpeedNode - halt')

        await self.publish_message(self.final_publication)  # must complete before super().halt() cancels tasks
        await super().halt()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def on_message(self):
        return self.__on_message


    @property
    def initial_publication(self):
        return self.__initial_publication


    @property
    def final_publication(self):
        return self.__final_publication


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        on_message = self.on_message.__name__
        routing_keys = '[' + ', '.join(map(str, self.subscription_routing_keys())) + ']'

        return (f'SpeedNode:{{routing_keys:{routing_keys}, on_message:{on_message}, '
                f'ops:{self.ops}, mq_client:{self.mq_client}}}')
