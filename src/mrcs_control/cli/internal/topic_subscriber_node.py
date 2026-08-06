"""
Created on 1 Aug 2026

@author: Bruno Beloff (bbeloff@me.com)

A simple subscriber node
"""

from mypy.nodes import Callable

from mrcs_control.messaging.mq_enums import MQTopology
from mrcs_control.operations.messaging_node import SubscriberNode
from mrcs_control.operations.node_enums import NodeTopology
from mrcs_core.data.equipment_identity import EquipmentIdentifier, EquipmentType
from mrcs_core.data.json import JSONable
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import SubscriptionRoutingKey


# --------------------------------------------------------------------------------------------------------------------

class TopicSubscriberNode(SubscriberNode):
    """
    a simple subscriber node
    """


    @classmethod
    def id(cls):
        return EquipmentIdentifier(EquipmentType.TST, None, 1)


    @classmethod
    def construct_node(cls, ops: NodeTopology.ServiceConfiguration, routing_keys: list[SubscriptionRoutingKey],
                       on_message: Callable[JSONable]):
        return cls(ops, MQTopology.MULTIPLE, cls.id(), routing_keys, on_message)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: NodeTopology.ServiceConfiguration, queuing: MQTopology, id: EquipmentIdentifier,
                 routing_keys: list[SubscriptionRoutingKey], on_message: Callable[JSONable]):
        super().__init__(ops, queuing, id)

        self.__routing_keys = routing_keys
        self.__on_message = on_message


    # ----------------------------------------------------------------------------------------------------------------

    def subscription_routing_keys(self):
        return self.routing_keys


    def handle_message(self, message: Message):
        self.on_message(message)


    # ----------------------------------------------------------------------------------------------------------------

    def subscribe(self):
        self.mq_client.connect()

        try:
            self.mq_client.subscribe(*self.subscription_routing_keys())
        except KeyboardInterrupt:
            return


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def routing_keys(self):
        return self.__routing_keys


    @property
    def on_message(self):
        return self.__on_message


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        on_message = self.on_message.__name__
        routing_keys = '[' + ', '.join([str(key) for key in self.routing_keys]) + ']'

        return (f'TopicSubscriberNode:{{routing_keys:{routing_keys}, on_message:{on_message}, '
                f'ops:{self.ops}, mq_client:{self.mq_client}}}')
