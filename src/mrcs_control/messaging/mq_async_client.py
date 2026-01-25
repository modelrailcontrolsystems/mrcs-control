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

from abc import ABC, abstractmethod
from typing import Callable

import pika
from pika.adapters.asyncio_connection import AsyncioConnection
from pika.exchange_type import ExchangeType

from mrcs_control.messaging.mq_client import MQMode

from mrcs_core.data.equipment_identity import EquipmentIdentifier
from mrcs_core.data.json import JSONify
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import SubscriptionRoutingKey
from mrcs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

class MQAsyncClient(ABC):
    """
    An abstract RabbitMQ client
    """

    __HOST = '127.0.0.1'  # do not use 'localhost' - IPv4 issues
    __PORT = 5672

    __URL = f'amqp://{__HOST}:{__PORT}/'


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, on_startup_complete: Callable | None = None):
        self.__on_startup_complete = on_startup_complete

        self.__connection = None
        self._channel = None
        self.__stopping = False

        self.__logger = Logging.getLogger()


    # ----------------------------------------------------------------------------------------------------------------

    def connect(self):
        self.logger.debug(f'connect - url:{self.__URL}')

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
        self.logger.debug(f'on_connection_open - connection:{connection}')

        self.__connection = connection
        self.__connection.channel(on_open_callback=self.on_channel_open)


    def on_connection_open_error(self, _unused_connection, err):
        self.logger.warning(f'on_connection_open_error - err:{err}')


    def on_connection_closed(self, _unused_connection, reason):
        self.logger.debug(f'on_connection_closed - reason:{reason}')
        self._channel = None


    @abstractmethod
    def on_channel_open(self, channel):  # TODO: need to call back from here before publishing?
        self.logger.debug(f'on_channel_open')
        pass


    def add_on_channel_close_callback(self):
        self.logger.debug(f'add_on_channel_close_callback')
        self.channel.add_on_close_callback(self.on_channel_closed)


    def on_channel_closed(self, _channel, reason):
        self.logger.debug(f'on_channel_closed - reason:{reason}')
        self._channel = None
        if not self.stopping:           # TODO: fix stopping
            self.connection.close()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def on_startup_complete(self):
        return self.__on_startup_complete


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


# --------------------------------------------------------------------------------------------------------------------

class MQAsyncPublisher(MQAsyncClient):
    """
    A RabbitMQ peer that can act as a publisher only
    """


    @classmethod
    def construct_pub(cls, exchange_name: MQMode, on_startup_complete: Callable | None = None):
        return cls(exchange_name, on_startup_complete=on_startup_complete)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, exchange_name, on_startup_complete: Callable | None = None):
        super().__init__(on_startup_complete=on_startup_complete)

        self.__exchange_name = exchange_name


    # ----------------------------------------------------------------------------------------------------------------

    def publish(self, message: Message):
        self.logger.debug(f'publish - message:{message}')

        if self.channel is None:
            raise RuntimeError('publish: no channel')

        if not self.channel.is_open:
            raise RuntimeError('publish: channel is not open')

        properties = pika.BasicProperties(
            content_type='application/json',
            delivery_mode=pika.DeliveryMode.Persistent)

        self.channel.basic_publish(exchange=self.exchange_name,
                                   routing_key=JSONify.as_jdict(message.routing_key),
                                   body=JSONify.dumps(message.payload),
                                   properties=properties)


    # ----------------------------------------------------------------------------------------------------------------

    def on_channel_open(self, channel):
        self.logger.debug(f'on_channel_open - channel:{channel}')

        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(self.exchange_name)


    def setup_exchange(self, exchange_name):
        self.logger.debug(f'setup_exchange - exchange_name:{exchange_name}')

        self.channel.exchange_declare(exchange=exchange_name, exchange_type=ExchangeType.topic, durable=True,
                                      callback=self.on_exchange_declare_ok)


    def on_exchange_declare_ok(self, _unused_frame):
        self.logger.debug(f'on_exchange_declare_ok')
        self.start_publishing()


    def start_publishing(self):
        self.logger.debug(f'start_publishing')
        self.channel.confirm_delivery(self.on_delivery_confirmation)


    def on_delivery_confirmation(self, method_frame):
        confirmation_type = method_frame.method.NAME.split('.')[1].lower()
        self.logger.debug(f'on_delivery_confirmation - confirmation_type:{confirmation_type}')


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def exchange_name(self):
        return self.__exchange_name


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'{self.__class__.__name__}:{{exchange_name:{self.exchange_name}}}'


# --------------------------------------------------------------------------------------------------------------------

class MQAsyncSubscriber(MQAsyncPublisher):
    """
    A RabbitMQ peer that can act as a publisher or subscriber
    """

    @classmethod
    def construct_sub(cls, exchange_name: MQMode, id: EquipmentIdentifier, on_message: Callable,
                      *subscription_routing_keys: SubscriptionRoutingKey,
                      on_startup_complete: Callable | None = None):
        queue = '.'.join([exchange_name, id.as_json()])

        return cls(exchange_name, id, queue, on_message,
                   *subscription_routing_keys, on_startup_complete=on_startup_complete)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, exchange_name, id: EquipmentIdentifier, queue, on_message: Callable,
                 *subscription_routing_keys: SubscriptionRoutingKey, on_startup_complete: Callable | None = None):
        super().__init__(exchange_name, on_startup_complete=on_startup_complete)

        self.__id = id
        self.__queue = queue
        self.__on_message = on_message
        self.__subscription_routing_keys = subscription_routing_keys


    # ----------------------------------------------------------------------------------------------------------------

    # subscribing is initiated with connect()

    def on_exchange_declare_ok(self, _unused_frame):
        self.logger.debug(f'on_exchange_declare_ok')
        self.setup_queue(self.queue)


    def setup_queue(self, queue_name):
        self.logger.debug(f'setup_queue - queue_name:{queue_name}')
        self.channel.queue_declare(queue=queue_name, durable=True, callback=self.on_queue_declare_ok)


    def on_queue_declare_ok(self, _unused_frame):
        self.logger.debug(f'on_queue_declare_ok - exchange_name:{self.exchange_name}, queue_name:{self.queue}')

        last_index = len(self.subscription_routing_keys) - 1
        for i, routing_key in enumerate(self.subscription_routing_keys):
            cb = functools.partial(self.on_bind_ok, start=i == last_index)
            self.channel.queue_bind(self.queue, self.exchange_name, routing_key=JSONify.as_jdict(routing_key),
                                    callback=cb)


    def on_bind_ok(self, _unused_frame, start):
        self.logger.debug(f'on_bind_ok')

        if start:
            self.logger.debug(f'on_bind_ok - starting')
            self.start_publishing()
            self.start_consuming()


    def start_consuming(self):
        self.logger.debug(f'start_consuming')

        self.add_on_cancel_callback()
        self.channel.basic_consume(self.queue, self.on_consume)

        if self.on_startup_complete is not None:
            self.on_startup_complete()


    def add_on_cancel_callback(self):
        self.logger.debug(f'add_on_cancel_callback')
        self.channel.add_on_cancel_callback(self.on_consumer_cancelled)


    def on_consumer_cancelled(self, method_frame):
        self.logger.debug(f'on_consumer_cancelled - method_frame:{method_frame}')
        self.channel.close()


    def acknowledge_message(self, delivery_tag):
        self.logger.debug(f'acknowledge_message - delivery_tag:{delivery_tag}')
        self.channel.basic_ack(delivery_tag)


    # ----------------------------------------------------------------------------------------------------------------

    def on_consume(self, _channel, delivery, _props, payload):
        self.logger.info(f'on_consume - delivery_tag:{delivery.delivery_tag}')

        routing_key = SubscriptionRoutingKey.construct_from_jdict(delivery.routing_key)

        if routing_key.source == self.id:
            return  # do not send message to self

        message = Message.construct_from_callback(routing_key, payload)
        self.on_message(message)

        self.acknowledge_message(delivery.delivery_tag)


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def id(self):
        return self.__id


    @property
    def queue(self):
        return self.__queue


    @property
    def on_message(self):
        return self.__on_message


    @property
    def subscription_routing_keys(self):
        return self.__subscription_routing_keys


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        routing_keys = [JSONify.as_jdict(key) for key in self.subscription_routing_keys]
        return (f'{self.__class__.__name__}:{{exchange_name:{self.exchange_name}, id:{self.id}, '
                f'queue:{self.queue}, channel:{self.channel}, routing_keys:{routing_keys}}}')
