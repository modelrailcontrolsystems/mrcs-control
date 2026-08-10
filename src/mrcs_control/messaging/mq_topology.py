"""
Created on 3 Aug 2026

@author: Bruno Beloff (bbeloff@me.com)

* MQMode - covers the TEST and LIVE cases

* QueueConfiguration - specifies how a queue should be configured for a given subscribing MQ client:

* MQTopology - anticipates the way in which an MQ subscriber client will be used. Two QueueConfiguration
options are supported:

    * SINGLE - used where there should only be one queue for a subscriber type. The queue should be durable,
    so that when the single subscriber is restarted, no messages will be lost. To support durability, the name of the
    queue should never change. Logically, the queue should be exclusive, but RabbitMQ does not support this arrangement.

    * MULTIPLE - used where multiple instances of a subscriber type are possible, an example is the
    mrcs_control_subscriber CLU. In that case, we can deliver to multiple mrcs_control_subscribers, each sharing a
    topic, but each client with its own queue. The subscriber's queue has a unique name, and is exclusive.
    The queue is discarded when the process terminates.

https://www.rabbitmq.com/tutorials
"""

from enum import Enum, StrEnum, unique
from uuid import uuid4

from mrcs_core.data.equipment_identity import EquipmentIdentifier
from mrcs_core.data.meta_enum import MetaEnum


# --------------------------------------------------------------------------------------------------------------------

@unique
class MQMode(StrEnum, metaclass=MetaEnum):
    """
    An enumeration of all the possible broker exchanges
    """

    TEST = 'mrcs.test'  # test mode
    LIVE = 'mrcs.live'  # production mode


# --------------------------------------------------------------------------------------------------------------------

@unique
class MQTopology(Enum, metaclass=MetaEnum):
    """
    An enumeration of all the supported queue topologies
    """


    # ----------------------------------------------------------------------------------------------------------------


    class QueueConfiguration(object):
        """
        The configuration of a queue for a subscriber
        """


        def __init__(self, unique_name: bool, durable: bool, exclusive: bool):
            self.__unique_name = unique_name
            self.__durable = durable
            self.__exclusive = exclusive

            self.__queue_name = None


        # ------------------------------------------------------------------------------------------------------------

        def queue_name(self, exchange_name: MQMode, id: EquipmentIdentifier) -> str:
            if self.__queue_name is not None:
                return self.__queue_name  # generate the name only once

            parts = [exchange_name, id.as_json()]

            if self.unique_name:
                parts.append(uuid4().hex)

            self.__queue_name = '.'.join(parts)
            return self.__queue_name


        # ------------------------------------------------------------------------------------------------------------

        @property
        def unique_name(self):
            return self.__unique_name


        @property
        def durable(self):
            return self.__durable


        @property
        def exclusive(self):
            return self.__exclusive


        # ------------------------------------------------------------------------------------------------------------

        def __str__(self, *args, **kwargs):
            return (f'MQMode.QueueConfiguration:{{unique_name:{self.unique_name}, durable:{self.durable}, '
                    f'exclusive:{self.exclusive}, queue_name:{self.__queue_name}}}')


    # ----------------------------------------------------------------------------------------------------------------

    SINGLE = QueueConfiguration(False, True, False)
    MULTIPLE = QueueConfiguration(True, False, True)
