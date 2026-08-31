"""
Created on 2 Jan 2026

@author: Bruno Beloff (bbeloff@me.com)

A simple subscriber node

Test with:
mrcs_publisher -vti4 -t CRN -n 3 -m '{"event_id": "abc", "on": "1930-01-02T06:25:00.000+00:00"}'
"""

from collections.abc import Callable
from typing import Any, Self

from mrcs_control.messaging.mq_topology import MQTopology
from mrcs_control.operations.async_messaging_node import AsyncSubscriberNode
from mrcs_control.operations.node_topology import NodeTopology
from mrcs_core.data.equipment_identity import EquipmentIdentifier, EquipmentType
from mrcs_core.data.json import JSONify
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import SubscriptionRoutingKey


# --------------------------------------------------------------------------------------------------------------------

class TopicSubscriberNode(AsyncSubscriberNode):
    """
    a simple subscriber node
    """

    __id = EquipmentIdentifier(EquipmentType.TST, None, 1)


    @classmethod
    def id(cls):
        return cls.__id


    @classmethod
    def set_id(cls, id: EquipmentIdentifier):
        cls.__id = id


    __routing_keys = []


    @classmethod
    def subscription_routing_keys(cls) -> list[SubscriptionRoutingKey]:
        return cls.__routing_keys


    @classmethod
    def set_subscription_routing_keys(cls, routing_keys: list[SubscriptionRoutingKey]):
        cls.__routing_keys = routing_keys


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def construct_node(cls, ops: NodeTopology.ServiceConfiguration,
                       on_message: Callable[[Message], Any]) -> Self:
        return cls(ops, MQTopology.MULTI_PROCESS, on_message)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: NodeTopology.ServiceConfiguration, queuing: MQTopology,
                 on_message: Callable[[Message], Any]):
        super().__init__(ops, queuing)
        self.__on_message = on_message
        self.__initial_publication: Message | None = None


    # ----------------------------------------------------------------------------------------------------------------

    def handle_startup(self):
        self.logger.debug('handle_startup')
        self.async_loop.create_task(self.publish_message())


    async def publish_message(self):
        self.logger.debug('publish_message')
        message = self.initial_publication
        if message is not None:
            self.async_loop.create_task(self.publish(message))


    def handle_message(self, message: Message):
        self.logger.debug(f'handle_message: {JSONify.as_jdict(message)}')
        self.on_message(message)


    # ----------------------------------------------------------------------------------------------------------------

    def run(self, initial_publication=None, *args, **kwargs) -> None:
        self.__initial_publication = initial_publication
        super().run(*args, **kwargs)


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def on_message(self):
        return self.__on_message


    @property
    def initial_publication(self):
        return self.__initial_publication


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        on_message = self.on_message.__name__
        routing_keys = '[' + ', '.join([str(key) for key in self.subscription_routing_keys()]) + ']'

        return (f'TopicSubscriberNode:{{routing_keys:{routing_keys}, on_message:{on_message}, '
                f'initial_publication:{self.initial_publication}, ops:{self.ops}, mq_client:{self.mq_client}}}')
