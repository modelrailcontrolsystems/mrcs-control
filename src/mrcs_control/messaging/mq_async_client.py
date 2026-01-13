"""
Created on 11 Jan 2026

@author: Bruno Beloff (bbeloff@me.com)

* MQAsyncClient - an abstract RabbitMQ client
* MQAsyncPublisher - a RabbitMQ peer that can act as a publisher only
* MQAsyncSubscriber - a RabbitMQ peer that can act as a publisher and subscriber

https://www.rabbitmq.com/tutorials/tutorial-four-python
https://github.com/aiidateam/aiida-core/issues/1142
https://stackoverflow.com/questions/15150207/connection-in-rabbitmq-server-auto-lost-after-600s
"""

import functools
import json

from abc import ABC, abstractmethod
from typing import Callable

import pika
from pika.adapters.asyncio_connection import AsyncioConnection
from pika.exchange_type import ExchangeType

from mrcs_control.messaging.mq_client import MQMode

from mrcs_core.data.equipment_identity import EquipmentIdentifier
from mrcs_core.data.json import JSONify
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import RoutingKey, SubscriptionRoutingKey
from mrcs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

class MQAsyncClient(ABC):
    """
    An abstract RabbitMQ client
    """

    __HOST = '127.0.0.1'            # do not use 'localhost' - IPv4 issues
    __PORT = 5672

    __URL = f'amqp://{__HOST}:{__PORT}/'

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self):
        self.__connection = None
        self._channel = None
        self.__stopping = False

        self.__logger = Logging.getLogger()


    # ----------------------------------------------------------------------------------------------------------------

    def connect(self):
        self.logger.info(f'connect - url:{self.__URL}')

        return AsyncioConnection(
            parameters=pika.URLParameters(self.__URL),
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed)


    def close(self):
        # TODO: implement close?
        pass


    # ----------------------------------------------------------------------------------------------------------------

    def on_connection_open(self, connection):
        self.logger.info(f'on_connection_open - connection:{connection}')

        self.__connection = connection
        self.__connection.channel(on_open_callback=self.on_channel_open)


    def on_connection_open_error(self, _unused_connection, err):
        self.logger.warning(f'on_connection_open_error - err:{err}')


    def on_connection_closed(self, _unused_connection, reason):
        self.logger.info(f'on_connection_closed - reason:{reason}')
        self._channel = None


    @abstractmethod
    def on_channel_open(self, channel):
        pass


    def add_on_channel_close_callback(self):
        self.logger.info(f'add_on_channel_close_callback')
        self.channel.add_on_close_callback(self.on_channel_closed)


    def on_channel_closed(self, _channel, reason):
        self.logger.info(f'on_channel_closed - reason:{reason}')
        self._channel = None
        if not self.stopping:
            self.connection.close()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def connection(self):
        return self.__connection


    @property
    def channel(self):
        return self._channel


    @property
    def stopping(self):
        return self.__stopping


    @property
    def logger(self):
        return self.__logger


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'MQClientAsync:{{connection:{self.connection}, channel:{self.channel}}}'


# --------------------------------------------------------------------------------------------------------------------

class MQAsyncPublisher(MQAsyncClient):
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

    def publish(self, message: Message):
        self.logger.info(f'publish - message:{message}')

        if self.channel is None:
            raise RuntimeError('publish: no channel')

        if not self.channel.is_open:
            raise RuntimeError('publish: channel is not open')

        properties = pika.BasicProperties(
            content_type='application/json',
            delivery_mode=pika.DeliveryMode.Persistent)

        self.channel.basic_publish(exchange=self.exchange_name,
                                   routing_key=message.routing_key.as_json(),
                                   body=JSONify.dumps(message.body),
                                   properties=properties)


    # ----------------------------------------------------------------------------------------------------------------

    def on_channel_open(self, channel):
        self.logger.info(f'on_channel_open - channel:{channel}')

        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(self.exchange_name)


    def setup_exchange(self, exchange_name):
        self.logger.info(f'setup_exchange - exchange_name:{exchange_name}')

        cb = functools.partial(self.on_exchange_declare_ok, userdata=exchange_name)
        self.channel.exchange_declare(exchange=exchange_name, exchange_type=ExchangeType.topic, durable=True,
                                      callback=cb)


    def on_exchange_declare_ok(self, _unused_frame, userdata):
        self.logger.info(f'on_exchange_declare_ok - userdata:{userdata}')
        self.start_publishing()


    def start_publishing(self):
        self.logger.info(f'start_publishing')
        self.channel.confirm_delivery(self.on_delivery_confirmation)


    def on_delivery_confirmation(self, method_frame):
        confirmation_type = method_frame.method.NAME.split('.')[1].lower()
        self.logger.info(f'on_delivery_confirmation - confirmation_type:{confirmation_type}')


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def exchange_name(self):
        return self.__exchange_name


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'MQAsyncPublisher:{{exchange_name:{self.exchange_name}}}'


# --------------------------------------------------------------------------------------------------------------------

class MQAsyncSubscriber(MQAsyncPublisher):
    """
    A RabbitMQ peer that can act as a publisher or subscriber
    """

    @classmethod
    def construct_sub(cls, exchange_name: MQMode, identity: EquipmentIdentifier, handle: Callable,
                      routing_key: RoutingKey):
        queue = '.'.join([exchange_name, identity.as_json()])

        return cls(exchange_name, identity, queue, handle, routing_key)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, exchange_name, identity: EquipmentIdentifier, queue, client_callback: Callable,
                 routing_key: RoutingKey):
        super().__init__(exchange_name)

        # TODO: support multiple routing_keys?

        self.__identity = identity                          # EquipmentIdentifier
        self.__queue = queue                                # string
        self.__client_callback = client_callback            # string
        self.__routing_key = routing_key                    # RoutingKey


    # ----------------------------------------------------------------------------------------------------------------

    # subscribing is initiated with connect()

    def on_exchange_declare_ok(self, _unused_frame, userdata):
        self.logger.info(f'on_exchange_declare_ok - userdata:{userdata}')
        self.setup_queue(self.queue)


    def setup_queue(self, queue_name):
        self.logger.info(f'setup_queue - queue_name:{queue_name}')
        self.channel.queue_declare(queue=queue_name, durable=True, callback=self.on_queue_declare_ok)


    def on_queue_declare_ok(self, _unused_frame):
        self.logger.info(f'on_queue_declare_ok - exchange_name:{self.exchange_name}, queue_name:{self.queue}, '
                         f'routing_key:{self.routing_key}')
        self.channel.queue_bind(self.queue, self.exchange_name, routing_key=JSONify.dumps(self.routing_key),
                                callback=self.on_bind_ok)


    def on_bind_ok(self, _unused_frame):
        self.logger.info(f'on_bind_ok')
        self.start_consuming()


    def start_consuming(self):
        self.logger.info(f'start_consuming')

        self.add_on_cancel_callback()
        self.channel.basic_consume(self.queue, self.on_message)


    def add_on_cancel_callback(self):
        self.logger.info(f'add_on_cancel_callback')
        self.channel.add_on_cancel_callback(self.on_consumer_cancelled)


    def on_consumer_cancelled(self, method_frame):
        self.logger.info(f'on_consumer_cancelled - method_frame:{method_frame}')
        self.channel.close()


    def acknowledge_message(self, delivery_tag):
        self.logger.info(f'acknowledge_message - delivery_tag:{delivery_tag}')
        self.channel.basic_ack(delivery_tag)


    # ----------------------------------------------------------------------------------------------------------------

    def on_message(self, _channel, delivery, _props, payload):
        self.logger.info(f'on_message - delivery_tag:{delivery.delivery_tag}')

        routing_key = SubscriptionRoutingKey.construct_from_jdict(json.loads(json.dumps(delivery.routing_key)))

        if routing_key.source == self.identity:
            return                                          # do not send message to self

        message = Message.construct_from_callback(routing_key, payload)
        self.client_callback(message)

        self.acknowledge_message(delivery.delivery_tag)


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def identity(self):
        return self.__identity


    @property
    def queue(self):
        return self.__queue


    @property
    def client_callback(self):
        return self.__client_callback


    @property
    def routing_key(self):
        return self.__routing_key


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'MQAsyncSubscriber:{{exchange_name:{self.exchange_name}, identity:{self.identity}, '
                f'queue:{self.queue}, channel:{self.channel}, routing_key:{self.routing_key}}}')
