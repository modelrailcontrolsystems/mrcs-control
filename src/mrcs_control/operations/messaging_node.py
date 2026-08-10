"""
Created on 4 Jan 2026

@author: Bruno Beloff (bbeloff@me.com)

Abstract blocking messaging nodes
"""
from abc import ABC, abstractmethod

from mrcs_control.messaging.mq_client import MQClient, MQPublisher, MQSubscriber
from mrcs_control.messaging.mq_topology import MQTopology
from mrcs_control.operations.node_topology import NodeTopology
from mrcs_core.data.equipment_identity import EquipmentIdentifier
from mrcs_core.data.json import JSONify
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import SubscriptionRoutingKey
from mrcs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

class MessagingNode(ABC):
    """
    An abstract blocking messaging node
    """


    @classmethod
    @abstractmethod
    def id(cls) -> EquipmentIdentifier:
        pass


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: NodeTopology.ServiceConfiguration, mq_client: MQClient):
        if not isinstance(ops, NodeTopology.ServiceConfiguration):
            raise TypeError(
                'ops must be a NodeTopology.ServiceConfiguration instance; '
                f'got {type(ops).__name__}. Use NodeTopology.<MODE>.value.'
            )

        self.__ops = ops
        self.__mq_client = mq_client

        self.__logger = Logging.getLogger()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def ops(self):
        return self.__ops


    @property
    def mq_client(self):
        return self.__mq_client


    @property
    def logger(self):
        return self.__logger


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'{self.__class__.__name__}:{{ops:{self.ops}, mq_client:{self.mq_client}}}'


# --------------------------------------------------------------------------------------------------------------------

class PublisherNode(MessagingNode, ABC):
    """
    a messaging node that can publish
    """


    @classmethod
    def construct(cls, ops: NodeTopology.ServiceConfiguration):
        return cls(ops)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: NodeTopology.ServiceConfiguration):
        mq_client = MQPublisher.construct_pub(ops.mq_mode)
        super().__init__(ops, mq_client)


# --------------------------------------------------------------------------------------------------------------------

class SubscriberNode(MessagingNode, ABC):
    """
    a blocking messaging node that can publish and subscribe
    """


    @classmethod
    @abstractmethod
    def subscription_routing_keys(cls) -> list[SubscriptionRoutingKey]:
        pass


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def construct(cls, ops: NodeTopology.ServiceConfiguration, queuing: MQTopology):
        return cls(ops, queuing)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: NodeTopology.ServiceConfiguration, queuing: MQTopology):
        mq_client = MQSubscriber.construct_sub(ops.mq_mode, queuing, self.id(), self.handle_message)
        super().__init__(ops, mq_client)


    # ----------------------------------------------------------------------------------------------------------------

    @abstractmethod
    def subscribe(self):
        pass


    @abstractmethod
    def handle_message(self, message: Message):
        pass


    # ----------------------------------------------------------------------------------------------------------------

    def close(self):
        self.mq_client.close()


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        routing_keys = [JSONify.as_jdict(key) for key in self.subscription_routing_keys()]

        return (f'{self.__class__.__name__}:{{routing_keys:{routing_keys}, '
                f'ops:{self.ops}, mq_client:{self.mq_client}}}')
