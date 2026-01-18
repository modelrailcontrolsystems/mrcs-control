"""
Created on 4 Jan 2026

@author: Bruno Beloff (bbeloff@me.com)

Abstract async messaging nodes
"""

from abc import ABC, abstractmethod

from mrcs_control.messaging.mq_async_client import MQAsyncSubscriber, MQAsyncPublisher
from mrcs_control.operations.operation_mode import OperationService

from mrcs_core.data.equipment_identity import EquipmentIdentifier
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import SubscriptionRoutingKey
from mrcs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

class AsyncMessagingNode(ABC):
    """
    An abstract async messaging node
    """

    @classmethod
    @abstractmethod
    def id(cls) -> EquipmentIdentifier:
        pass

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: OperationService, mq_client):
        self.__ops = ops
        self.__mq_client = mq_client

        self.__logger = Logging.getLogger()


    # ----------------------------------------------------------------------------------------------------------------

    def connect(self):
        self.mq_client.connect()


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

class AsyncPublisherNode(AsyncMessagingNode, ABC):
    """
    an async messaging node that can publish
    """

    def __init__(self, ops: OperationService):
        super().__init__(ops, MQAsyncPublisher.construct_pub(ops.mq_mode))


    # ----------------------------------------------------------------------------------------------------------------

    def publish(self, message: Message):
        self.mq_client.publish(message)


# --------------------------------------------------------------------------------------------------------------------

class AsyncSubscriberNode(AsyncMessagingNode, ABC):
    """
    an async messaging node that can publish and subscribe
    """

    @classmethod
    @abstractmethod
    def subscription_routing_keys(cls) -> list[SubscriptionRoutingKey]:
        pass


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: OperationService):
        super().__init__(ops, MQAsyncSubscriber.construct_sub(ops.mq_mode, self.id(), self.handle,
                                                              *self.subscription_routing_keys()))


    # ----------------------------------------------------------------------------------------------------------------

    @abstractmethod
    def handle(self, message: Message):
        pass


    def publish(self, message: Message):
        self.mq_client.publish(message)
