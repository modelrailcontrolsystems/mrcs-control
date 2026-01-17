"""
Created on 4 Jan 2026

@author: Bruno Beloff (bbeloff@me.com)

Abstract messaging nodes
"""

from abc import ABC, abstractmethod

from mrcs_control.messaging.mq_async_client import MQAsyncClient, MQAsyncSubscriber, MQAsyncPublisher
from mrcs_control.operations.operation_mode import OperationMode, OperationService

from mrcs_core.data.equipment_identity import EquipmentIdentifier
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import SubscriptionRoutingKey
from mrcs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

class AsyncMessagingNode(ABC):
    """
    An abstract messaging node
    """

    @classmethod
    @abstractmethod
    def identity(cls) -> EquipmentIdentifier:
        pass

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: OperationService, mq_client: MQAsyncClient):
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
        return f'{self.__class__.__name__}:{{identity:{self.identity()}, ops:{self.ops}, mq_client:{self.mq_client}}}'


# --------------------------------------------------------------------------------------------------------------------

class AsyncPublisherNode(AsyncMessagingNode, ABC):
    """
    A messaging node that can publish
    """

    @classmethod
    def construct(cls, ops_mode: OperationMode):
        return cls(ops_mode.value)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: OperationService):
        super().__init__(ops, MQAsyncPublisher.construct_pub(ops.mq_mode))


# --------------------------------------------------------------------------------------------------------------------

class AsyncSubscriberNode(AsyncMessagingNode, ABC):
    """
    A messaging node that can publish and subscribe
    """

    @classmethod
    @abstractmethod
    def routing_keys(cls) -> list[SubscriptionRoutingKey]:
        pass


    @classmethod
    def construct(cls, ops_mode: OperationMode):
        return cls(ops_mode.value)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: OperationService):
        super().__init__(ops, MQAsyncSubscriber.construct_sub(ops.mq_mode, self.identity(), self.handle,
                                                              *self.routing_keys()))


    # ----------------------------------------------------------------------------------------------------------------

    @abstractmethod
    def handle(self, message: Message):
        pass


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'{self.__class__.__name__}:{{identity:{self.identity()}, ops:{self.ops}, mq_client:{self.mq_client}}}'
