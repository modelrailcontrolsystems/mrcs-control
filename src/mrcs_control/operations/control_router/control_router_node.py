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
from mrcs_control.operations.control_router.control_router_identity import ControlRouterIdentity
from mrcs_control.operations.control_router.control_router_state import ControlRouterState
from mrcs_core.data.json import JSONable
from mrcs_core.equipment.control_router.control_router_conf import ControlRouterConf
from mrcs_core.equipment.control_router.control_router_report import ControlRouterReport
from mrcs_core.equipment.equipment_enums import CRT, EquipmentType
from mrcs_core.equipment.equipment_identity import EquipmentFilter, EquipmentIdentifier
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import PublicationRoutingKey, SubscriptionRoutingKey
from mrcs_core.operations.node_topology import NodeTopology
from mrcs_core.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

class ControlRouterNode(AsyncSubscriberNode):
    """
    an interface between a Z21 control router and the messaging system
    """

    __KEEP_ALIVE_INTERVAL = 10.0  # seconds
    __RETRY_INTERVAL = 5.0  # seconds


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def id(cls):
        return EquipmentIdentifier(EquipmentType.CRT, None, CRT.ROUTER)


    @classmethod
    def subscription_routing_keys(cls) -> list[SubscriptionRoutingKey]:
        return [SubscriptionRoutingKey(EquipmentFilter.any(), cls.id()), ]


    @classmethod
    def equipment(cls) -> ControlRouterReport:
        return PersistentControlRouter.load(Host)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: NodeTopology.ServiceConfiguration,
                 conf: ControlRouterConf, on_message: Callable[JSONable] | None = None):
        super().__init__(ops, MQTopology.SINGLE_PROCESS)

        self.__conf = conf
        self.__on_message = on_message

        self.__state = ControlRouterState()
        self.__monitor_task = None
        self.__monitor_exception: BaseException | None = None


    # ----------------------------------------------------------------------------------------------------------------
    # messaging handlers...

    def handle_startup(self):
        self.logger.debug('ControlRouterNode - handle_startup')

        if self.monitor_task is None:
            self.__monitor_task = self.async_loop.create_task(self.monitor())
            self.__monitor_task.add_done_callback(self.__on_monitor_done)


    def __on_monitor_done(self, task: asyncio.Task):
        if task.cancelled() or task.exception() is None:
            return

        self.__monitor_exception = task.exception()
        self.request_shutdown()


    async def handle_message(self, message: Message):
        self.logger.debug('ControlRouterNode - handle_message')

        await self.state.wait_until_router_is_available()

        try:
            command = Command.construct_from_jdict(message.body)
            await self.state.router.send_command(command)
        except Exception as exc:
            self.logger.warning(f'handle_message:{type(exc).__name__}:{exc} on:{message}')

        if self.on_message:
            self.on_message(message)


    def run(self, *args, **kwargs) -> None:
        self.logger.debug('ControlRouterNode - run')
        super().run(*args, **kwargs)

        if self.monitor_exception is not None:
            raise self.monitor_exception


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
        if self.state.is_READY():
            self.logger.warn('connection lost')

        self.state.go_UNAVAILABLE()


    # ----------------------------------------------------------------------------------------------------------------

    async def monitor(self) -> None:
        self.logger.debug('ControlRouterNode - monitor')

        while True:
            try:
                async with Station(self.conf, self.on_dataset, self.on_connection_lost) as station:
                    await station.connect()
                    await station.send_command(Command.lan_set_broadcast_flags(self.conf.subscription))
                    await station.get_system_state()

                    self.state.go_READY(station)
                    self.logger.info('ready')

                    while self.state.is_READY():
                        await asyncio.sleep(self.__KEEP_ALIVE_INTERVAL)
                        await station.get_system_state()

            except asyncio.CancelledError:
                self.logger.error('monitor cancelled')
                raise

            except RuntimeError as exc:
                self.logger.error(f'monitor: {exc}')
                raise

            except Exception as exc:
                self.logger.debug(f'monitor: {type(exc).__name__}: {exc}')
                await asyncio.sleep(self.__RETRY_INTERVAL)

            finally:
                self.state.go_STANDBY()


    # ----------------------------------------------------------------------------------------------------------------

    async def halt(self) -> None:
        self.logger.debug('ControlRouterNode - halt')

        await self.shutdown()
        await super().halt()


    async def shutdown(self) -> None:
        self.logger.debug('ControlRouterNode - shutdown')

        task = self.monitor_task
        if task is not None and not task.done() and task is not asyncio.current_task():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass


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
    def state(self):
        return self.__state


    @property
    def monitor_task(self):
        return self.__monitor_task


    @property
    def monitor_exception(self):
        return self.__monitor_exception


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        on_message = None if self.on_message.__name__ is not None else self.on_message.__name__
        routing_keys = '[' + ', '.join(map(str, self.subscription_routing_keys())) + ']'

        return (f'ControlRouterNode:{{conf:{self.conf}, routing_keys:{routing_keys}, on_message:{on_message}, '
                f'state:{self.state}, ops:{self.ops}, mq_client:{self.mq_client}}}')
