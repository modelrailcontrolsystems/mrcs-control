"""
Created on 4 Jan 2026

@author: Bruno Beloff (bbeloff@me.com)

Abstract messaging nodes
"""

from abc import ABC, abstractmethod

from mrcs_control.messaging.mq_client import MQPublisher, MQSubscriber, MQClient
from mrcs_control.operations.operation_mode import OperationMode, OperationService

from mrcs_core.data.equipment_identity import EquipmentIdentifier
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import SubscriptionRoutingKey
from mrcs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

class MessagingNode(ABC):
    """
    An abstract messaging node
    """

    @classmethod
    @abstractmethod
    def identity(cls) -> EquipmentIdentifier:
        pass

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: OperationService, mq_client: MQClient):
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

class PublisherNode(MessagingNode, ABC):
    """
    A messaging node that can publish
    """

    @classmethod
    def construct(cls, ops_mode: OperationMode):
        return cls(ops_mode.value)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: OperationService):
        super().__init__(ops, MQPublisher.construct_pub(ops.mq_mode))


# --------------------------------------------------------------------------------------------------------------------

class SubscriberNode(MessagingNode, ABC):
    """
    A messaging node that can publish and subscribe
    """

    @classmethod
    def construct(cls, ops_mode: OperationMode):
        return cls(ops_mode.value)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: OperationService):
        super().__init__(ops, MQSubscriber.construct_sub(ops.mq_mode, self.identity(), self.handle))


    # ----------------------------------------------------------------------------------------------------------------

    @abstractmethod
    def routing_keys(self) -> list[SubscriptionRoutingKey]:
        pass


    @abstractmethod
    def subscribe(self):
        pass


    @abstractmethod
    def handle(self, message: Message):
        pass


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'{self.__class__.__name__}:{{identity:{self.identity()}, routing_keys:{self.routing_keys()}, '
                f'ops:{self.ops}, mq_client:{self.mq_client}}}')
