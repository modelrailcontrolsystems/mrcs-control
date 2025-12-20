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

import pika
from pika.exceptions import AMQPError

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
        self._logger = Logging.getLogger()


    # ----------------------------------------------------------------------------------------------------------------

    def connect(self):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.__DEFAULT_HOST),
        )

        self.__channel = connection.channel()


    def close(self):
        try:
            if self.channel is None:
                return False

            self.channel.close()
            return True

        except AMQPError as ex:
            self._logger.warn(f'close: {ex.__class__.__name__}:{ex}')
            return False

        finally:
            self.__channel = None


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def channel(self):
        return self.__channel


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'Client:{{channel:{self.channel}}}'


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
        if self.channel is None:
            raise RuntimeError('exchange_delete: no channel')

        self.channel.exchange_delete(exchange=exchange, if_unused=True)


    def queue_delete(self, queue):
        if self.channel is None:
            raise RuntimeError('queue_delete: no channel')

        self.channel.queue_delete(queue, if_unused=True, if_empty=False)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'Manager:{{channel:{self.channel}}}'


# --------------------------------------------------------------------------------------------------------------------

class Publisher(MQClient):
    """
    A RabbitMQ peer that can act as a publisher only
    """

    __EXCHANGE_TYPE = 'topic'


    @classmethod
    def construct_pub(cls, exchange_name: MQMode):
        return cls(exchange_name)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, exchange_name):
        super().__init__()

        self.__exchange_name = exchange_name                      # string


    # ----------------------------------------------------------------------------------------------------------------

    def connect(self):
        super().connect()
        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type=self.__EXCHANGE_TYPE, durable=True)


    def publish(self, message: Message):
        if self.channel is None:
            raise RuntimeError('publish: no channel')

        while True:
            try:
                self.channel.basic_publish(
                    exchange=self.exchange_name,
                    routing_key=message.routing_key.as_json(),
                    body=JSONify.dumps(message.body),
                    properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent)
                )
                break

            except AMQPError:
                self.close()
                self.connect()
                self._logger.warn('publish: connection re-established')


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def exchange_name(self):
        return self.__exchange_name


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'Publisher:{{exchange_name:{self.exchange_name}, channel:{self.channel}}}'


# --------------------------------------------------------------------------------------------------------------------

class Subscriber(Publisher):
    """
    A RabbitMQ peer that can act as a publisher and subscriber
    """

    @classmethod
    def construct_sub(cls, exchange_name: MQMode, identity: EquipmentIdentifier, callback):
        queue = '.'.join([exchange_name, identity.as_json()])

        return cls(exchange_name, identity, queue, callback)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, exchange_name, identity, queue, callback):
        super().__init__(exchange_name)

        self.__identity = identity                      # EquipmentIdentifier
        self.__queue = queue                            # string
        self.__callback = callback                      # string


    # ----------------------------------------------------------------------------------------------------------------

    def subscribe(self, *routing_keys: RoutingKey):
        if self.channel is None:
            raise RuntimeError('subscribe: no channel')

        if self.identity is None:
            raise RuntimeError('subscribe: no identity')

        if self.queue is None:
            raise RuntimeError('subscribe: no queue')

        if self.callback is None:
            raise RuntimeError('subscribe: no callback')

        if not routing_keys:
            raise RuntimeError('subscribe: no routing keys')

        self.channel.queue_declare(self.queue, durable=True, exclusive=False)   # durables may not be exclusive

        for routing_key in routing_keys:
            self.channel.queue_bind(
                exchange=self.exchange_name,
                queue=self.queue,
                routing_key=routing_key.as_json(),
            )

        self.channel.basic_consume(
            queue=self.queue,
            on_message_callback=self.on_message_callback,
        )

        self.channel.start_consuming()


    def on_message_callback(self, ch, method, _properties, body):
        routing_key = PublicationRoutingKey.construct_from_jdict(method.routing_key)
        if routing_key.source == self.identity:
            return                                          # do not send message to self

        self.callback(Message.construct_from_callback(routing_key, body))

        ch.basic_ack(delivery_tag=method.delivery_tag)      # ACK will not take place if callback raises an exception


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def identity(self):
        return self.__identity


    @property
    def queue(self):
        return self.__queue


    @property
    def callback(self):
        return self.__callback


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'Subscriber:{{exchange_name:{self.exchange_name}, identity:{self.identity}, queue:{self.queue}, '
                f'callback:{self.callback}, channel:{self.channel}}}')
