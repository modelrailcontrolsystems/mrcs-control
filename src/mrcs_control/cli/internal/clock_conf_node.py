"""
Created on 22 Jan 2026

@author: Bruno Beloff (bbeloff@me.com)

An AsyncSubscriberNode that requests clock conf changes to the clock manager node.
Implements a single-shot interlock that waits for the clock manager to respond.
"""

from mrcs_control.messaging.mq_topology import MQTopology
from mrcs_control.operations.async_messaging_node import AsyncSubscriberNode
from mrcs_control.operations.node_topology import NodeTopology
from mrcs_control.operations.time.clock_manager_node import ClockManagerNode
from mrcs_control.operations.time.cron_serial import CronSerial
from mrcs_core.data.equipment_identity import EquipmentFilter, EquipmentIdentifier, EquipmentType
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import PublicationRoutingKey, SubscriptionRoutingKey
from mrcs_core.operations.time.clock import Clock


# --------------------------------------------------------------------------------------------------------------------

class ClockConfNode(AsyncSubscriberNode):
    """
    an authority for clock configuration
    """


    @classmethod
    def id(cls):
        return EquipmentIdentifier(EquipmentType.CLK, None, CronSerial.CLOCK_CONF)


    @classmethod
    def subscription_routing_keys(cls) -> list[SubscriptionRoutingKey]:
        return [SubscriptionRoutingKey(ClockManagerNode.id(), EquipmentFilter.any())]


    @classmethod
    def publication_routing_key(cls):
        return PublicationRoutingKey(cls.id(), ClockManagerNode.id())


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: NodeTopology.ServiceConfiguration, clock: Clock):
        super().__init__(ops, MQTopology.SINGLE_PROCESS)

        self.__clock = clock
        self.__origin = None


    # ----------------------------------------------------------------------------------------------------------------

    def handle_startup(self):
        self.logger.info('handle_startup')
        self.async_loop.create_task(self.publish_clock())


    def handle_message(self, message: Message):
        if message.origin == self.origin:
            self.async_loop.create_task(self.halt())


    # ----------------------------------------------------------------------------------------------------------------

    async def publish_clock(self):
        message = Message(self.publication_routing_key(), self.clock)
        self.__origin = message.origin

        await self.publish(message)


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def clock(self):
        return self.__clock


    @property
    def origin(self):
        return self.__origin


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'ClockConfNode:{{clock:{self.clock}, ops:{self.ops}, mq_client:{self.mq_client}}}'
