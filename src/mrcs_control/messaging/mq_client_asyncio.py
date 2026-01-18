"""
Created on 11 Jan 2026

@author: jpmckinney, lukebakken, David Taylor, Bruno Beloff (bbeloff@me.com)

Deprecated - replaced with MQAsyncClient


https://stackoverflow.com/questions/70889479/how-to-use-pika-with-fastapis-asyncio-loop
https://github.com/pika/pika/blob/main/examples/asynchronous_publisher_example.py
https://github.com/pika/pika/blob/main/examples/asynchronous_consumer_example.py
"""

import functools
import json
from typing import Callable

import pika
from pika.adapters.asyncio_connection import AsyncioConnection
from pika.exchange_type import ExchangeType
from typing_extensions import deprecated

from mrcs_control.messaging.mq_client import MQMode

from mrcs_core.data.equipment_identity import EquipmentIdentifier
from mrcs_core.data.json import JSONify
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import SubscriptionRoutingKey
from mrcs_core.sys.logging import Logging


# ----------------------------------------------------------------------------------------------------------------

@deprecated
class MQClientAsync(object):
    URL = 'amqp://127.0.0.1:5672/%2F'
    EXCHANGE_TYPE = ExchangeType.topic
    PUBLISH_INTERVAL = 1
    ROUTING_KEY = 'TST.*.001.API.*.001'


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def construct(cls, exchange_name: MQMode, id: EquipmentIdentifier, handle: Callable):
        queue = '.'.join([exchange_name.value, id.as_json()])

        return cls(exchange_name, id, queue, handle)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, exchange_name, id: EquipmentIdentifier, queue, client_callback: Callable):
        self.__exchange_name = exchange_name            # string
        self.__id = id                                  # EquipmentIdentifier
        self.__queue = queue                            # string
        self.__client_callback = client_callback        # Callable

        self.should_reconnect = False
        self.was_consuming = False

        self._connection = None
        self._channel = None
        self._stopping = False      # TODO: handle this properly
        self._consumer_tag = None
        self._consuming = False

        self.__logger = Logging.getLogger()


    # ----------------------------------------------------------------------------------------------------------------

    def subscription_callback(self, _channel, delivery, _props, payload):
        self.logger.debug(f'subscription_callback - delivery:{delivery}')

        routing_key = SubscriptionRoutingKey.construct_from_jdict(json.loads(f'"{delivery.routing_key}"'))
        message = Message.construct_from_callback(routing_key, payload)
        self.logger.debug(f'subscription_callback - message:{message}')

        self.client_callback(message)

        self.acknowledge_message(delivery.delivery_tag)


    # ----------------------------------------------------------------------------------------------------------------

    def connect(self):
        self.logger.debug(f'connect - url:{self.URL}')

        return AsyncioConnection(
            parameters=pika.URLParameters(self.URL),
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed)


    def on_connection_open(self, connection):
        self.logger.debug(f'on_connection_open - connection:{connection}')
        self._connection = connection

        channel = self._connection.channel(on_open_callback=self.on_channel_open)
        self.logger.debug(f'on_connection_open - channel:{channel}')


    def on_connection_open_error(self, _unused_connection, err):
        self.logger.debug(f'on_connection_open_error - err:{err}')

    # TODO: may need close_connection()

    def on_connection_closed(self, _unused_connection, reason):
        self.logger.debug(f'on_connection_closed - reason:{reason}')
        self._channel = None

    # TODO: may need reconnect()

    def on_channel_open(self, channel):
        self.logger.debug(f'on_channel_open - channel:{channel}')
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(self.exchange_name)


    def add_on_channel_close_callback(self):
        self.logger.debug(f'add_on_channel_close_callback')
        self._channel.add_on_close_callback(self.on_channel_closed)


    def on_channel_closed(self, _channel, reason):
        self.logger.debug(f'on_channel_closed - reason:{reason}')
        self._channel = None
        if not self._stopping:
            self._connection.close()


    def setup_exchange(self, exchange_name):
        self.logger.debug(f'setup_exchange - exchange_name:{exchange_name}')
        # Note: using functools.partial is not required, it is demonstrating
        # how arbitrary data can be passed to the callback when it is called
        cb = functools.partial(self.on_exchange_declare_ok, userdata=exchange_name)
        self._channel.exchange_declare(exchange=exchange_name, exchange_type=self.EXCHANGE_TYPE, durable=True,
                                       callback=cb)


    def on_exchange_declare_ok(self, _unused_frame, userdata):
        self.logger.debug(f'on_exchange_declare_ok - userdata:{userdata}')
        self.setup_queue(self.queue)


    def setup_queue(self, queue_name):
        self.logger.debug(f'setup_queue - queue_name:{queue_name}')
        self._channel.queue_declare(queue=queue_name, durable=True, callback=self.on_queue_declare_ok)


    def on_queue_declare_ok(self, _unused_frame):
        self.logger.debug(f'on_queue_declare_ok - exchange_name:{self.exchange_name}, queue_name:{self.queue}, '
                          f'routing_key:{self.ROUTING_KEY}')
        self._channel.queue_bind(self.queue, self.exchange_name, routing_key=self.ROUTING_KEY, callback=self.on_bind_ok)


    def on_bind_ok(self, _unused_frame):
        self.logger.debug(f'on_bind_ok')
        # self.start_publishing()       # TODO: refactor to two client subtypes?
        self.start_consuming()


    def start_consuming(self):
        self.logger.debug(f'start_consuming')

        self.add_on_cancel_callback()
        self._consumer_tag = self._channel.basic_consume(self.queue, self.subscription_callback)
        self.was_consuming = True
        self._consuming = True


    def add_on_cancel_callback(self):
        self.logger.debug(f'add_on_cancel_callback')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)


    def on_consumer_cancelled(self, method_frame):
        self.logger.debug(f'on_consumer_cancelled - method_frame:{method_frame}')
        self._channel.close()


    def on_message(self, _unused_channel, basic_deliver, properties, body):
        self.logger.debug(f'on_message - delivery_tag:{basic_deliver.delivery_tag}, '
                          f'app_id:{properties.app_id}, body:{body}')
        self.acknowledge_message(basic_deliver.delivery_tag)


    def acknowledge_message(self, delivery_tag):
        self.logger.debug(f'acknowledge_message - acknowledge_message:{delivery_tag}')
        self._channel.basic_ack(delivery_tag)


    def start_publishing(self):
        self.logger.debug(f'start_publishing')
        self._channel.confirm_delivery(self.on_delivery_confirmation)


    def publish_message(self, message: Message):
        self.logger.debug(f'publish_message - message:{message}')
        if self._channel is None:
            raise RuntimeError('publish_message: no channel')

        if not self._channel.is_open:
            raise RuntimeError('publish_message: channel is not open')

        properties = pika.BasicProperties(
            content_type='application/json',
            delivery_mode=pika.DeliveryMode.Persistent)

        self._channel.basic_publish(exchange=self.exchange_name,
                                    routing_key=message.routing_key.as_json(),
                                    body=JSONify.dumps(message.body),
                                    properties=properties)

        self.logger.debug(f'publish_message - published')


    def on_delivery_confirmation(self, method_frame):
        confirmation_type = method_frame.method.NAME.split('.')[1].lower()
        self.logger.debug(f'on_delivery_confirmation - confirmation_type:{confirmation_type}')


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def exchange_name(self):
        return self.__exchange_name


    @property
    def client_callback(self):
        return self.__client_callback


    @property
    def id(self):
        return self.__id


    @property
    def queue(self):
        return self.__queue


    @property
    def logger(self):
        return self.__logger


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'MQClientAsync:{{exchange_name:{self.exchange_name}, id:{self.id}, queue:{self.queue}}}'
