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

    __id = EquipmentIdentifier(EquipmentType.TST, None, 1)


    @classmethod
    def id(cls):
        return cls.__id


    @classmethod
    def set_id(cls, id: EquipmentIdentifier):
        cls.__id = id


    __routing_keys = []


    @classmethod
    def subscription_routing_keys(cls):
        return cls.__routing_keys


    @classmethod
    def set_subscription_routing_keys(cls, routing_keys: list[SubscriptionRoutingKey]):
        cls.__routing_keys = routing_keys


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def construct_node(cls, ops: NodeTopology.ServiceConfiguration, on_message: Callable[JSONable]):
        return cls(ops, MQTopology.MULTIPLE, on_message)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: NodeTopology.ServiceConfiguration, queuing: MQTopology, on_message: Callable[JSONable]):
        super().__init__(ops, queuing)
        self.__on_message = on_message


    # ----------------------------------------------------------------------------------------------------------------

    def handle_startup(self):
        self.logger.info('TopicSubscriberNode - handle_startup')


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
    def on_message(self):
        return self.__on_message


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        on_message = self.on_message.__name__
        routing_keys = '[' + ', '.join([str(key) for key in self.subscription_routing_keys()]) + ']'

        return (f'TopicSubscriberNode:{{routing_keys:{routing_keys}, on_message:{on_message}, '
                f'ops:{self.ops}, mq_client:{self.mq_client}}}')
