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
from collections.abc import Callable
from typing import Self

import pika
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection
from pika.exceptions import AMQPError, ChannelWrongStateError
from pika.exchange_type import ExchangeType

from mrcs_control.messaging.mq_topology import MQMode, MQTopology
from mrcs_core.data.equipment_identity import EquipmentIdentifier
from mrcs_core.data.json import JSONify
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import PublicationRoutingKey, RoutingKey
from mrcs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

class MQClient(ABC):
    """
    An abstract RabbitMQ client
    """

    __DEFAULT_HOST = '127.0.0.1'  # do not use localhost - IPv6 issues


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self):
        self.__connection = None
        self.__channel = None
        self.__logger = Logging.getLogger()


    # ----------------------------------------------------------------------------------------------------------------

    def connect(self) -> None:
        self.logger.debug('MQClient - connect')

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.__DEFAULT_HOST),
        )

        self.channel = self.connection.channel()


    def close(self) -> bool:
        self.logger.debug('close')

        try:
            if self.channel is not None and self.channel.is_open:
                self.channel.close()
            if self.connection is not None and self.connection.is_open:
                self.connection.close()
            return True
        except (AttributeError, ChannelWrongStateError):
            return False

        except AMQPError as exc:
            self.logger.warn(f'close:{exc.__class__.__name__}:{exc}')
            return False

        finally:
            self.channel = None
            self.connection = None


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def is_connected(self) -> bool:
        return self.channel is not None


    @property
    def connection(self) -> BlockingConnection:
        return self.__connection


    @connection.setter
    def connection(self, connection: BlockingConnection | None) -> None:
        self.__connection = connection


    @property
    def channel(self) -> BlockingChannel:
        return self.__channel


    @channel.setter
    def channel(self, channel: BlockingChannel | None) -> None:
        self.__channel = channel


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

    def exchange_delete(self, exchange_name: str):
        self.logger.debug(f'MQManager - exchange_delete:{exchange_name}')

        if self.channel is None:
            raise RuntimeError('exchange_delete: no channel')

        self.channel.exchange_delete(exchange=exchange_name, if_unused=True)


    def queue_declare(self, queue_name: str, durable: bool = False, exclusive: bool = False,
                      auto_delete: bool = False) -> None:
        self.logger.debug(f'MQManager - queue_declare:{queue_name}')

        if self.channel is None:
            raise RuntimeError('queue_declare: no channel')

        self.channel.queue_declare(
            queue=queue_name,
            durable=durable,
            exclusive=exclusive,
            auto_delete=auto_delete,
        )


    def queue_delete(self, queue_name: str):
        self.logger.debug(f'MQManager - queue_delete:{queue_name}')

        if self.channel is None:
            raise RuntimeError('queue_delete: no channel')

        self.channel.queue_delete(queue_name, if_unused=True)


    def queue_purge(self, queue_name: str) -> int:
        self.logger.debug(f'MQManager - queue_purge:{queue_name}')

        if self.channel is None:
            raise RuntimeError('queue_purge: no channel')

        response = self.channel.queue_purge(queue_name)
        return response.method.message_count


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'MQManager:{{channel:{self.channel}}}'


# --------------------------------------------------------------------------------------------------------------------

class MQPublisher(MQClient):
    """
    A RabbitMQ peer that can act as a publisher only
    """


    @classmethod
    def construct_pub(cls, exchange_name: MQMode) -> Self:
        return cls(exchange_name)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, exchange_name: MQMode):
        super().__init__()

        self.__exchange_name = exchange_name  # string


    # ----------------------------------------------------------------------------------------------------------------

    def connect(self):
        self.logger.debug(f'MQPublisher - connect')

        super().connect()
        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type=ExchangeType.topic, durable=True)
        self.logger.debug(f'connect - channel:{self.channel}')


    def publish(self, message: Message):
        self.logger.debug(f'MQPublisher - publish:{message}')

        try:
            routing_key = JSONify.as_jdict(message.routing_key)
        except Exception:
            self.logger.warn(f'publish - invalid routing_key:{message.routing_key}')
            return

        try:
            body = JSONify.dumps(message.payload)
        except Exception:
            self.logger.warn(f'publish - invalid body:{message.payload}')
            return

        while True:
            try:
                properties = pika.BasicProperties(
                    content_type='application/json',
                    delivery_mode=pika.DeliveryMode.Persistent)

                self.channel.basic_publish(
                    exchange=self.exchange_name,
                    routing_key=routing_key,
                    body=body,
                    properties=properties)
                break

            except (AttributeError, AMQPError) as exc:
                self.logger.info(f'publish - conect failed:{exc}')
                self.close()
                self.connect()
                self.logger.info('publish - connection re-established')


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
    def construct_sub(cls, exchange_name: MQMode, queuing: MQTopology, id: EquipmentIdentifier,
                      on_message: Callable) -> Self:
        return cls(exchange_name, queuing.value, id, on_message)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, exchange_name: MQMode, queue_config: MQTopology.QueueConfiguration, id: EquipmentIdentifier,
                 on_message: Callable):
        super().__init__(exchange_name)

        self.__id = id
        self.__queue_config = queue_config
        self.__on_message = on_message


    # ----------------------------------------------------------------------------------------------------------------

    def queue_purge(self) -> int:
        self.logger.debug(f'MQSubscriber - queue_purge:{self.queue_name}')

        if self.channel is None:
            raise RuntimeError('queue_purge: no channel')

        self.channel.queue_declare(
            self.queue_name,
            durable=self.queue_config.durable,
            exclusive=self.queue_config.exclusive,
        )

        response = self.channel.queue_purge(self.queue_name)
        return response.method.message_count


    def subscribe(self, *routing_keys: RoutingKey):
        self.logger.debug('subscribe')

        if self.channel is None:
            raise RuntimeError('subscribe: no channel')

        if not routing_keys:
            raise RuntimeError('subscribe: no routing keys')

        durable = self.queue_config.durable
        exclusive = self.queue_config.exclusive

        while True:
            try:
                self.channel.queue_declare(self.queue_name, durable=durable, exclusive=exclusive)

                for routing_key in routing_keys:
                    self.channel.queue_bind(
                        exchange=self.exchange_name,
                        queue=self.queue_name,
                        routing_key=routing_key.as_json(),
                    )

                self.channel.basic_consume(
                    queue=self.queue_name,
                    on_message_callback=self.on_consume,
                )

                self.channel.start_consuming()
            except AMQPError as exc:
                self.logger.info(f'subscribe - conect failed:{exc}')
                self.close()
                self.connect()
                self.logger.info('subscribe - connection re-established')


    def on_consume(self, ch, method, _properties, payload):
        self.logger.debug(f'MQSubscriber - on_consume:{method.delivery_tag}')

        try:
            routing_key = PublicationRoutingKey.construct_from_jdict(method.routing_key)
        except Exception:
            self.logger.warn(f'on_consume - invalid routing_key:{method.routing_key}')
            return

        if routing_key.source == self.id:
            return  # do not send message to self

        message = Message.construct_from_callback(routing_key, payload)

        try:
            self.on_message_message(message)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as exc:
            self.logger.warn(f'on_consume:{type(exc).__name__}:{exc} - message:{message}')
            # ch.basic_nack(delivery_tag=method.delivery_tag)   # TODO: enable as required


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def id(self):
        return self.__id


    @property
    def queue_config(self):
        return self.__queue_config


    @property
    def queue_name(self):
        return self.queue_config.queue_name(self.exchange_name, self.id)


    @property
    def on_message_message(self):
        return self.__on_message


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'MQSubscriber:{{exchange_name:{self.exchange_name}, id:{self.id}, queue_config:{self.queue_config}, '
                f'queue_name:{self.queue_name}, channel:{self.channel}}}')
