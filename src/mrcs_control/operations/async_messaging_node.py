"""
Created on 4 Jan 2026

@author: Bruno Beloff (bbeloff@me.com)

Abstract async messaging nodes

The AsyncMessagingNode class provides asyncio loop utilities to support concrete node operations.
"""

import asyncio
import signal
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from mrcs_control.messaging.mq_async_client import MQAsyncClient, MQAsyncPublisher, MQAsyncSubscriber
from mrcs_control.messaging.mq_client import MQManager
from mrcs_control.messaging.mq_topology import MQTopology
from mrcs_core.equipment.equipment_identity import EquipmentIdentifier
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import SubscriptionRoutingKey
from mrcs_core.operations.node_topology import NodeTopology
from mrcs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

AsyncClientT = TypeVar('AsyncClientT', bound=MQAsyncClient)


# --------------------------------------------------------------------------------------------------------------------


class AsyncMessagingNode(Generic[AsyncClientT], ABC):
    """
    An abstract async messaging node
    """


    @classmethod
    @abstractmethod
    def id(cls) -> EquipmentIdentifier:
        pass


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: NodeTopology.ServiceConfiguration, mq_client: AsyncClientT):
        if not isinstance(ops, NodeTopology.ServiceConfiguration):
            raise TypeError(
                'ops must be a NodeTopology.ServiceConfiguration instance; '
                f'got {type(ops).__name__}. Use NodeTopology.<MODE>.value.'
            )

        self.__ops = ops
        self.__mq_client = mq_client
        self.__interrupted = False

        self.__logger = Logging.getLogger()


    # ----------------------------------------------------------------------------------------------------------------

    @abstractmethod
    def run(self, *args, **kwargs) -> None:
        pass


    @abstractmethod
    async def halt(self) -> None:
        pass


    @property
    @abstractmethod
    def async_loop(self) -> asyncio.AbstractEventLoop:
        pass


    # ----------------------------------------------------------------------------------------------------------------

    def connect(self):
        self.mq_client.connect()


    def handle_startup(self):
        pass


    def run_async_loop(self):
        self.__interrupted = False

        asyncio.set_event_loop(self.async_loop)
        self.install_signal_handlers()

        try:
            self.connect()
            self.async_loop.run_forever()

        finally:
            # if the loop was left without halt() - e.g. exit() in a message handler - halt while the loop can
            # still run, so that any final publication is sent and the connection is closed
            if self.mq_client.connection is not None:
                try:
                    self.async_loop.run_until_complete(self.halt())
                except Exception as exc:
                    # do not mask the exception that ended the loop
                    self.logger.warning(f'run_async_loop - halt:{type(exc).__name__}:{exc}')

            # restore default SIGINT / SIGTERM behaviour once the loop is no longer running
            self.remove_signal_handlers()
            self.async_loop.close()
            asyncio.set_event_loop(None)

        if self.interrupted:
            raise KeyboardInterrupt


    def install_signal_handlers(self):
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                self.async_loop.add_signal_handler(sig, self.handle_signal)
            except (NotImplementedError, RuntimeError):
                # Signal handlers are unavailable outside the main thread or on
                # platforms that do not support asyncio signal handlers.
                pass


    def remove_signal_handlers(self):
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                self.async_loop.remove_signal_handler(sig)
            except (NotImplementedError, RuntimeError):
                pass


    def handle_signal(self):
        self.__interrupted = True
        self.request_shutdown()


    def close(self) -> None:
        self.logger.debug('AsyncMessagingNode - close')

        if self.mq_client is not None:
            self.mq_client.close()


    def request_shutdown(self):
        if self.async_loop is not None and self.async_loop.is_running():
            self.async_loop.create_task(self.halt())


    async def cancel_tasks(self):
        current = asyncio.current_task()
        tasks = [task for task in asyncio.all_tasks(self.async_loop) if task is not current]

        for task in tasks:
            task.cancel()

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)


    # ----------------------------------------------------------------------------------------------------------------

    async def connection_is_available(self):
        await self.mq_client.connection_is_available()


    # ----------------------------------------------------------------------------------------------------------------


    @property
    def ops(self):
        return self.__ops


    @property
    def mq_client(self) -> AsyncClientT:
        return self.__mq_client


    @mq_client.setter
    def mq_client(self, mq_client: AsyncClientT):
        self.__mq_client = mq_client


    @property
    def interrupted(self) -> bool:
        return self.__interrupted


    @property
    def logger(self):
        return self.__logger


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'{self.__class__.__name__}:{{ops:{self.ops}, mq_client:{self.mq_client}}}'


# --------------------------------------------------------------------------------------------------------------------

class AsyncPublisherNode(AsyncMessagingNode[MQAsyncPublisher], ABC):
    """
    an async messaging node that can publish
    """


    def __init__(self, ops: NodeTopology.ServiceConfiguration):
        publisher = MQAsyncPublisher.construct_pub(ops.mq_mode, on_startup_complete=self.handle_startup)
        super().__init__(ops, publisher)
        self.__async_loop = None


    # ----------------------------------------------------------------------------------------------------------------

    async def publish(self, message: Message):
        self.logger.debug('AsyncPublisherNode - publish')
        await self.mq_client.publish(message)


    # ----------------------------------------------------------------------------------------------------------------

    def run(self, *args, **kwargs) -> None:
        self.logger.debug('AsyncPublisherNode - run')

        self.__async_loop = asyncio.new_event_loop()
        self.run_async_loop()


    async def halt(self):
        self.logger.debug('AsyncPublisherNode - halt')

        await self.cancel_tasks()
        await self.mq_client.close_and_wait()
        self.async_loop.stop()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def async_loop(self):
        return self.__async_loop


# --------------------------------------------------------------------------------------------------------------------

class AsyncSubscriberNode(AsyncMessagingNode[MQAsyncSubscriber], ABC):
    """
    an async messaging node that can publish and subscribe
    """


    @classmethod
    @abstractmethod
    def subscription_routing_keys(cls) -> list[SubscriptionRoutingKey]:
        pass


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: NodeTopology.ServiceConfiguration, queuing: MQTopology):
        subscriber = MQAsyncSubscriber.construct_sub(ops.mq_mode, queuing, self.id(), self.handle_message,
                                                     *self.subscription_routing_keys(),
                                                     on_startup_complete=self.handle_startup)
        super().__init__(ops, subscriber)
        self.__async_loop = None


    # ----------------------------------------------------------------------------------------------------------------

    @abstractmethod
    def handle_message(self, message: Message) -> None:
        pass


    # ----------------------------------------------------------------------------------------------------------------

    async def publish(self, message: Message):
        self.logger.debug('AsyncSubscriberNode - publish')
        await self.mq_client.publish(message)


    # ----------------------------------------------------------------------------------------------------------------

    def drain(self) -> int | None:
        self.logger.debug('AsyncSubscriberNode - drain')

        if self.mq_client.queue_config.exclusive:
            return None

        manager = MQManager()
        manager.connect()

        try:
            manager.queue_declare(
                self.mq_client.queue_name,
                durable=self.mq_client.queue_config.durable,
                exclusive=self.mq_client.queue_config.exclusive,
            )

            return manager.queue_purge(self.mq_client.queue_name)

        finally:
            manager.close()


    def run(self, *args, **kwargs) -> None:
        self.logger.debug('AsyncSubscriberNode - run')

        self.__async_loop = asyncio.new_event_loop()
        self.run_async_loop()


    async def halt(self) -> None:
        self.logger.debug('AsyncSubscriberNode - halt')
        await self.cancel_tasks()
        await self.mq_client.close_and_wait()
        self.async_loop.stop()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def async_loop(self):
        return self.__async_loop
