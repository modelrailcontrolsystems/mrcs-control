"""
Created on 1 Nov 2025

@author: Bruno Beloff (bbeloff@me.com)

* Client - an abstract RabbitMQ client
* Manager - a Client that can perform broker management tasks
* Publisher - a RabbitMQ peer that can act as a publisher only
* Subscriber - a RabbitMQ peer that can act as a publisher and subscriber

https://www.rabbitmq.com/tutorials/tutorial-four-python
https://github.com/aiidateam/aiida-core/issues/1142
https://stackoverflow.com/questions/15150207/connection-in-rabbitmq-server-auto-lost-after-600s
"""

from abc import ABC
from enum import unique, StrEnum
from typing import Callable

import pika
from pika.exceptions import AMQPError, ChannelWrongStateError
from pika.exchange_type import ExchangeType

from mrcs_core.data.equipment_identity import EquipmentIdentifier
from mrcs_core.data.json import JSONify
from mrcs_core.data.meta_enum import MetaEnum
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import RoutingKey, PublicationRoutingKey
from mrcs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

@unique
class MQMode(StrEnum, metaclass=MetaEnum):
    """
    An enumeration of all the possible broker exchanges
    """

    TEST = 'mrcs.test'  # test mode
    LIVE = 'mrcs.live'  # production mode


# --------------------------------------------------------------------------------------------------------------------

class MQClient(ABC):
    """
    An abstract RabbitMQ client
    """

    __DEFAULT_HOST = '127.0.0.1'                # do not use localhost - IPv6 issues

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self):
        self.__channel = None
        self.__logger = Logging.getLogger()


    # ----------------------------------------------------------------------------------------------------------------

    def connect(self):
        self.logger.debug('connect')

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.__DEFAULT_HOST),
        )

        self.__channel = connection.channel()


    def close(self):
        self.logger.debug('close')

        try:
            self.channel.close()
            return True
        except (AttributeError, ChannelWrongStateError):
            return False

        except AMQPError as ex:
            self.logger.warn(f'close: {ex.__class__.__name__}:{ex}')
            return False

        finally:
            self.__channel = None


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def channel(self):
        return self.__channel


    @property
    def logger(self):
        return self.__logger


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'MQClient:{{channel:{self.channel}}}'


# --------------------------------------------------------------------------------------------------------------------

class MQManager(MQClient):
    """
    A Client that can perform broker management tasks
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self):
        super().__init__()


    # ----------------------------------------------------------------------------------------------------------------

    def exchange_delete(self, exchange):
        self.logger.debug(f'exchange_delete:{exchange}')

        if self.channel is None:
            raise RuntimeError('exchange_delete: no channel')

        self.channel.exchange_delete(exchange=exchange, if_unused=True)


    def queue_delete(self, queue):
        self.logger.debug(f'queue_delete:{queue}')

        if self.channel is None:
            raise RuntimeError('queue_delete: no channel')

        self.channel.queue_delete(queue, if_unused=True, if_empty=False)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'MQManager:{{channel:{self.channel}}}'


# --------------------------------------------------------------------------------------------------------------------

class MQPublisher(MQClient):
    """
    A RabbitMQ peer that can act as a publisher only
    """

    @classmethod
    def construct_pub(cls, exchange_name: MQMode):
        return cls(exchange_name)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, exchange_name):
        super().__init__()

        self.__exchange_name = exchange_name                      # string


    # ----------------------------------------------------------------------------------------------------------------

    def connect(self):
        self.logger.debug(f'connect')

        super().connect()
        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type=ExchangeType.topic, durable=True)
        self.logger.debug(f'connect - channel:{self.channel}')


    def publish(self, message: Message):
        self.logger.debug(f'publish - message:{message}')

        while True:
            try:
                properties = pika.BasicProperties(
                    content_type='application/json',
                    delivery_mode=pika.DeliveryMode.Persistent)

                self.channel.basic_publish(
                    exchange=self.exchange_name,
                    routing_key=JSONify.as_jdict(message.routing_key),
                    body=JSONify.dumps(message.payload),
                    properties=properties)
                break

            except (AttributeError, AMQPError):
                self.logger.warn('* B * remaking connection')
                self.close()
                self.connect()

                self.logger.warn('* B * connection re-established')


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def exchange_name(self):
        return self.__exchange_name


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'MQPublisher:{{exchange_name:{self.exchange_name}}}'


# --------------------------------------------------------------------------------------------------------------------

class MQSubscriber(MQPublisher):
    """
    A RabbitMQ peer that can act as a publisher and subscriber
    """

    @classmethod
    def construct_sub(cls, exchange_name: MQMode, id: EquipmentIdentifier, on_message: Callable):
        queue = '.'.join([exchange_name, id.as_json()])

        return cls(exchange_name, id, queue, on_message)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, exchange_name, id: EquipmentIdentifier, queue, on_message: Callable):
        super().__init__(exchange_name)

        self.__id = id
        self.__queue = queue
        self.__on_message = on_message


    # ----------------------------------------------------------------------------------------------------------------

    def subscribe(self, *routing_keys: RoutingKey):
        self.logger.debug('subscribe')

        if self.channel is None:
            raise RuntimeError('subscribe: no channel')

        if self.queue is None:
            raise RuntimeError('subscribe: no queue')

        if not routing_keys:
            raise RuntimeError('subscribe: no routing keys')

        while True:
            try:
                self.channel.queue_declare(self.queue, durable=True, exclusive=False)  # durables may not be exclusive

                for routing_key in routing_keys:
                    self.channel.queue_bind(
                        exchange=self.exchange_name,
                        queue=self.queue,
                        routing_key=routing_key.as_json(),
                    )

                self.channel.basic_consume(
                    queue=self.queue,
                    on_message_callback=self.on_consume,
                )

                self.channel.start_consuming()
            except AMQPError:
                self.close()
                self.connect()
                self.logger.warn('subscribe: connection re-established')


    def on_consume(self, ch, method, _properties, payload):
        self.logger.debug(f'on_consume - payload:{str(payload)}')

        routing_key = PublicationRoutingKey.construct_from_jdict(method.routing_key)

        if routing_key.source == self.id:
            return                                          # do not send message to self

        message = Message.construct_from_callback(routing_key, payload)

        self.on_message_message(message)

        ch.basic_ack(delivery_tag=method.delivery_tag)      # ACK will not take place if callback raises an exception


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def id(self):
        return self.__id


    @property
    def queue(self):
        return self.__queue


    @property
    def on_message_message(self):
        return self.__on_message


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'MQSubscriber:{{exchange_name:{self.exchange_name}, id:{self.id}, queue:{self.queue}, '
                f'channel:{self.channel}}}')
