"""
Created on 31 Jul 2026

@author: Bruno Beloff (bbeloff@me.com)

An AsyncPublisherNode that implements an interface between a Z21 control router and the messaging system.

Commands may be sent to the control router station via the ControlRouterNode subscriber, datasets that are
produced by the station are published.

In this implementation, the ControlRouterNode runs a keep-alive. If this fails, then the station is marked as
unavailable. In this case, subsequent command messages remain on the queue. Once the station is available again,
those command messages are processed. Messages that are received while the station is unavailable - but before its
unavailabily is determined - may be lost.

Test with:
mrcs_control_router -t -r -v
mrcs_control_subscriber -t -v   -s 'CRT.*.*'
mrcs_control_publisher -t -v -r 'CRT.*.1' -m '{"type": "XCommand", "x_header": "LAN_X_SET_TRACK_POWER", "argv": [129]}'
"""

import asyncio
from collections.abc import Callable

from mrcs_control.dcc.z21.command.command import Command
from mrcs_control.dcc.z21.command.station import Station
from mrcs_control.equipment.control_router.persistent_control_router import PersistentControlRouter
from mrcs_control.messaging.mq_topology import MQTopology
from mrcs_control.operations.async_messaging_node import AsyncSubscriberNode
from mrcs_control.operations.control_router.control_router_identity import ControlRouterIdentity, ControlRouterSerial
from mrcs_control.operations.node_topology import NodeTopology
from mrcs_core.data.equipment_identity import EquipmentFilter, EquipmentIdentifier, EquipmentType
from mrcs_core.data.json import JSONable
from mrcs_core.equipment.control_router.control_router_conf import ControlRouterConf
from mrcs_core.equipment.control_router.control_router_report import ControlRouterReport
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import PublicationRoutingKey, SubscriptionRoutingKey
from mrcs_core.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

class ControlRouterNode(AsyncSubscriberNode):
    """
    an interface between a Z21 control router and the messaging system
    """

    __KEEP_ALIVE_INTERVAL = 30.0  # seconds
    __RETRY_INTERVAL = 5.0  # seconds


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def id(cls):
        return EquipmentIdentifier(EquipmentType.CRT, None, ControlRouterSerial.Router)


    @classmethod
    def subscription_routing_keys(cls) -> list[SubscriptionRoutingKey]:
        return [SubscriptionRoutingKey(EquipmentFilter.any(), cls.id()), ]


    @classmethod
    def state(cls) -> ControlRouterReport:
        return PersistentControlRouter.load(Host)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: NodeTopology.ServiceConfiguration,
                 conf: ControlRouterConf, on_message: Callable[JSONable] | None = None):
        super().__init__(ops, MQTopology.SINGLE_PROCESS)

        self.__conf = conf
        self.__on_message = on_message

        self.__station = None
        self.__monitor_task = None
        self.__station_ready = False
        self.__station_ready_event = asyncio.Event()


    # ----------------------------------------------------------------------------------------------------------------
    # messaging handlers...

    def handle_startup(self):
        self.logger.debug('ControlRouterNode - handle_startup')

        if self.__monitor_task is None:
            self.__monitor_task = self.async_loop.create_task(self.monitor())


    async def handle_message(self, message: Message):
        self.logger.debug('ControlRouterNode - handle_message')

        if self.on_message:
            self.on_message(message)

        await self.__wait_until_station_ready()

        try:
            command = Command.construct_from_jdict(message.body)
            await self.station.send_command(command)
        except Exception as exc:
            self.logger.warning(f'handle_message:{type(exc).__name__}:{exc} on:{message}')


    def run(self, *args, **kwargs) -> None:
        self.logger.debug('ControlRouterNode - run')
        super().run(*args, **kwargs)


    async def __wait_until_station_ready(self):
        await self.__station_ready_event.wait()


    # ----------------------------------------------------------------------------------------------------------------
    # control router handlers...

    def on_dataset(self, report: JSONable):
        self.logger.debug(f'ControlRouterNode - on_dataset:{report}')

        if isinstance(report, ControlRouterReport):
            PersistentControlRouter.narrow(report).save(Host)

        source = ControlRouterIdentity.get(report)
        routing_key = PublicationRoutingKey(source, EquipmentFilter.any())

        outgoing = Message(routing_key, report)
        self.async_loop.create_task(self.mq_client.publish(outgoing))


    def on_connection_lost(self):
        self.station_ready = False
        self.logger.debug('ControlRouterNode - on_connection_lost')


    # ----------------------------------------------------------------------------------------------------------------

    async def monitor(self) -> None:
        self.logger.debug('ControlRouterNode - monitor')

        while True:
            try:
                async with Station(self.conf, self.on_dataset, self.on_connection_lost) as station:
                    self.__station = station
                    await self.station.connect()
                    await self.station.send_command(Command.lan_set_broadcast_flags(self.conf.subscription))
                    await self.station.get_system_state()
                    self.station_ready = True

                    while True:
                        await asyncio.sleep(self.__KEEP_ALIVE_INTERVAL)
                        await self.station.get_system_state()

            except ConnectionError as exc:
                self.logger.warning(f'connection error: {exc}')
                self.station_ready = False
                await asyncio.sleep(self.__RETRY_INTERVAL)

            except asyncio.CancelledError:
                self.logger.warning('monitor cancelled')
                raise

            except Exception as exc:
                self.station_ready = False
                self.logger.warning(f'monitor exception: {type(exc).__name__}: {exc}')
                await asyncio.sleep(self.__RETRY_INTERVAL)

            finally:
                self.station_ready = False
                self.__station = None


    async def halt(self) -> None:
        self.logger.debug('ControlRouterNode - halt')

        await self.shutdown()
        await super().halt()


    async def shutdown(self) -> None:
        self.logger.debug('shutdown')

        task = self.__monitor_task
        if task is not None and not task.done() and task is not asyncio.current_task():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        if task is not None and task.done() and not task.cancelled():
            exception = task.exception()
            if exception is not None:
                raise exception


    def close(self) -> None:
        self.logger.debug('ControlRouterNode - close')

        if self.async_loop is not None and self.async_loop.is_closed():
            return

        if self.async_loop is None or self.async_loop.is_running():
            # If the node is running, shutdown must be awaited by the loop.
            if self.async_loop is not None:
                self.async_loop.create_task(self.shutdown())
            return

        self.async_loop.run_until_complete(self.shutdown())
        self.logger.info('closed')


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def conf(self):
        return self.__conf


    @property
    def on_message(self):
        return self.__on_message


    @property
    def station(self):
        return self.__station


    @property
    def station_ready(self):
        return self.__station_ready


    @station_ready.setter
    def station_ready(self, ready: bool):
        if ready == self.__station_ready:
            return

        self.__station_ready = ready
        self.logger.info(f'station_ready:{self.station_ready}')

        if ready:
            self.__station_ready_event.set()
        else:
            self.__station_ready_event.clear()


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        on_message = None if self.on_message.__name__ is not None else self.on_message.__name__
        routing_keys = '[' + ', '.join([str(key) for key in self.subscription_routing_keys()]) + ']'

        return (f'ControlRouterNode:{{conf:{self.conf}, routing_keys:{routing_keys}, on_message:{on_message}, '
                f'station:{self.station}, station_ready:{self.station_ready}, '
                f'ops:{self.ops}, mq_client:{self.mq_client}}}')
