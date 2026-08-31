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

import asyncio
import functools
import inspect
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Self

import pika
from pika.adapters.asyncio_connection import AsyncioConnection
from pika.exceptions import AMQPError, ChannelWrongStateError
from pika.exchange_type import ExchangeType

from mrcs_control.messaging.mq_client import MQMode
from mrcs_control.messaging.mq_topology import MQTopology
from mrcs_core.data.equipment_identity import EquipmentIdentifier
from mrcs_core.data.json import JSONify
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import PublicationRoutingKey, SubscriptionRoutingKey
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
        self._is_connected = False

        self.__logger = Logging.getLogger()


    # ----------------------------------------------------------------------------------------------------------------

    @abstractmethod
    def on_channel_open(self, channel):
        pass


    # ----------------------------------------------------------------------------------------------------------------

    def connect(self):
        self.logger.debug(f'MQAsyncClient - connect:{self.__URL}')

        AsyncioConnection(
            parameters=pika.URLParameters(self.__URL),
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed)


    def close(self):
        if self.connection is None and self.channel is None:
            return

        self.logger.debug(f'MQAsyncClient - close:{self.__URL}')

        try:
            self.channel.close()
        except (AttributeError, ChannelWrongStateError):
            pass

        finally:
            self._channel = None

        try:
            self.connection.close()
        except (AttributeError, AMQPError):
            pass

        finally:
            self.__connection = None


    # ----------------------------------------------------------------------------------------------------------------

    async def connection_is_available(self):
        while not self._is_connected:
            await asyncio.sleep(0.1)


    # ----------------------------------------------------------------------------------------------------------------

    def on_connection_open(self, connection):
        self.logger.debug(f'MQAsyncClient - on_connection_open:{connection}')

        self.__connection = connection
        self.__connection.channel(on_open_callback=self.on_channel_open)


    def on_connection_open_error(self, _unused_connection, err):
        self.logger.warning(f'on_connection_open_error:{err}')


    def on_connection_closed(self, _unused_connection, reason):
        self.logger.debug(f'MQAsyncClient - on_connection_closed{reason}')
        self._channel = None


    def add_on_channel_close_callback(self):
        self.logger.debug(f'MQAsyncClient - add_on_channel_close_callback')
        self.channel.add_on_close_callback(self.on_channel_closed)


    def on_channel_closed(self, _channel, reason):
        self.logger.debug(f'MQAsyncClient - on_channel_closed:{reason}')

        self._channel = None
        self.connection.close()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def on_startup_complete(self):
        self._is_connected = True
        return self.__on_startup_complete


    @property
    def connection(self):
        return self.__connection


    @property
    def channel(self):
        return self._channel


    @property
    def logger(self):
        return self.__logger


# --------------------------------------------------------------------------------------------------------------------

class MQAsyncPublisher(MQAsyncClient):
    """
    A RabbitMQ peer that can act as a publisher only
    """


    @classmethod
    def construct_pub(cls, exchange_name: MQMode, on_startup_complete: Callable | None = None) -> Self:
        return cls(exchange_name, on_startup_complete=on_startup_complete)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, exchange_name: MQMode, on_startup_complete: Callable | None = None):
        super().__init__(on_startup_complete=on_startup_complete)
        self.__exchange_name = exchange_name


    # ----------------------------------------------------------------------------------------------------------------

    async def publish(self, message: Message):
        self.logger.debug(f'MQAsyncPublisher - publish:{message}')

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

            except (AttributeError, AMQPError, RuntimeError):
                self.logger.info('remaking connection')
                self._is_connected = False
                self.close()
                self.connect()
                await self.connection_is_available()
                self.logger.info('connection re-established')


    # ----------------------------------------------------------------------------------------------------------------

    def on_channel_open(self, channel):
        self.logger.debug(f'MQAsyncPublisher - on_channel_open:{channel}')

        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(self.exchange_name)


    def setup_exchange(self, exchange_name):
        self.logger.debug(f'MQAsyncPublisher - setup_exchange:{exchange_name}')

        self.channel.exchange_declare(exchange=exchange_name, exchange_type=ExchangeType.topic, durable=True,
                                      callback=self.on_exchange_declare_ok)


    def on_exchange_declare_ok(self, _unused_frame):
        self.logger.debug(f'MQAsyncPublisher - on_exchange_declare_ok')
        self.start_publishing()


    def start_publishing(self, notify_startup=True):
        self.logger.debug(f'MQAsyncPublisher - start_publishing')

        self.channel.confirm_delivery(self.on_delivery_confirmation)
        self._is_connected = True

        if notify_startup and self.on_startup_complete is not None:
            self.on_startup_complete()


    def on_delivery_confirmation(self, method_frame):
        confirmation_type = method_frame.method.NAME.split('.')[1].lower()
        self.logger.debug(f'MQAsyncPublisher - on_delivery_confirmation:{confirmation_type}')


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def exchange_name(self):
        return self.__exchange_name


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'{self.__class__.__name__}:{{exchange_name:{self.exchange_name}, is_connected:{self._is_connected}}}'


# --------------------------------------------------------------------------------------------------------------------

class MQAsyncSubscriber(MQAsyncPublisher):
    """
    A RabbitMQ peer that can act as a publisher or subscriber
    """


    @classmethod
    def construct_sub(cls, exchange_name: MQMode, queuing: MQTopology, id: EquipmentIdentifier, on_message: Callable,
                      *subscription_routing_keys: SubscriptionRoutingKey,
                      on_startup_complete: Callable | None = None) -> Self:

        return cls(exchange_name, id, queuing.value, on_message,
                   *subscription_routing_keys, on_startup_complete=on_startup_complete)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, exchange_name: MQMode, id: EquipmentIdentifier, queue_config: MQTopology.QueueConfiguration,
                 on_message: Callable, *subscription_routing_keys: SubscriptionRoutingKey,
                 on_startup_complete: Callable | None = None):
        super().__init__(exchange_name, on_startup_complete=on_startup_complete)

        self.__id = id
        self.__queue_config = queue_config
        self.__on_message = on_message
        self.__subscription_routing_keys = subscription_routing_keys


    # ----------------------------------------------------------------------------------------------------------------

    # subscribing is initiated with connect()

    def on_exchange_declare_ok(self, _unused_frame):
        self.logger.debug('MQAsyncSubscriber - on_exchange_declare_ok')
        self.setup_queue()


    def setup_queue(self):
        self.logger.debug(f'MQAsyncSubscriber - setup_queue:{self.queue_name}')

        durable = self.queue_config.durable
        exclusive = self.queue_config.exclusive

        self.channel.queue_declare(queue=self.queue_name, durable=durable, exclusive=exclusive, auto_delete=False,
                                   callback=self.on_queue_declare_ok)


    def on_queue_declare_ok(self, _unused_frame):
        self.logger.debug(f'MQAsyncSubscriber - on_queue_declare_ok - exchange_name:{self.exchange_name}, '
                          f'queue_name:{self.queue_name}')

        last_index = len(self.subscription_routing_keys) - 1
        for i, routing_key in enumerate(self.subscription_routing_keys):
            cb = functools.partial(self.on_bind_ok, start=i == last_index)
            self.channel.queue_bind(self.queue_name, self.exchange_name, routing_key=JSONify.as_jdict(routing_key),
                                    callback=cb)


    def on_bind_ok(self, _unused_frame, start):
        self.logger.debug('MQAsyncSubscriber - on_bind_ok')

        if start:
            self.logger.debug('MQAsyncSubscriber - on_bind_ok - starting')
            self.start_publishing(notify_startup=False)
            self.start_consuming()


    def start_consuming(self):
        self.logger.debug('MQAsyncSubscriber - start_consuming')

        self.add_on_cancel_callback()
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.queue_name, self.on_consume)

        if self.on_startup_complete is not None:
            self.on_startup_complete()


    def add_on_cancel_callback(self):
        self.logger.debug('MQAsyncSubscriber - add_on_cancel_callback')
        self.channel.add_on_cancel_callback(self.on_consumer_cancelled)


    def on_consumer_cancelled(self, method_frame):
        self.logger.debug(f'MQAsyncSubscriber - on_consumer_cancelled:{method_frame}')
        self.channel.close()


    def acknowledge_message(self, delivery_tag):
        self.logger.debug(f'MQAsyncSubscriber - acknowledge_message:{delivery_tag}')
        self.channel.basic_ack(delivery_tag)


    # ----------------------------------------------------------------------------------------------------------------

    def on_consume(self, _channel, delivery, _props, payload):
        self.logger.debug(f'MQAsyncSubscriber - on_consume:{delivery.delivery_tag}')

        try:
            routing_key = PublicationRoutingKey.construct_from_jdict(delivery.routing_key)
        except Exception:
            self.logger.warn(f'on_consume - invalid routing_key:{delivery.routing_key}')
            return

        if routing_key.source == self.id:
            self.acknowledge_message(delivery.delivery_tag)
            return  # do not send message to self

        message = Message.construct_from_callback(routing_key, payload)
        asyncio.create_task(self.process_message(delivery.delivery_tag, message))


    async def process_message(self, delivery_tag, message):
        self.logger.debug(f'MQAsyncSubscriber - process_message:{message}')

        try:
            result = self.on_message(message)
            if inspect.isawaitable(result):
                await result

            self.acknowledge_message(delivery_tag)

        except Exception as exc:
            self.logger.warn(f'process_message:{type(exc).__name__}:{exc} - message:{message}')
            # Leave the message unacknowledged so it is requeued when the channel closes.


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
    def on_message(self):
        return self.__on_message


    @property
    def subscription_routing_keys(self) -> list[SubscriptionRoutingKey]:
        return list(self.__subscription_routing_keys)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        routing_keys = [JSONify.as_jdict(key) for key in self.subscription_routing_keys]

        return (f'{self.__class__.__name__}:{{exchange_name:{self.exchange_name}, is_connected:{self._is_connected}, '
                f'id:{self.id}, queue_config:{self.queue_config}, queue_name:{self.queue_name}, '
                f'channel:{self.channel}, routing_keys:{routing_keys}}}')
