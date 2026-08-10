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

from mrcs_control.dcc.z21.command.command import Command
from mrcs_control.dcc.z21.command.station import Station
from mrcs_control.equipment.control_router.control_router_identity import ControlRouterIdentity
from mrcs_control.messaging.mq_enums import MQTopology
from mrcs_control.operations.async_messaging_node import AsyncSubscriberNode
from mrcs_control.operations.node_enums import NodeTopology
from mrcs_core.data.equipment_identity import EquipmentFilter, EquipmentIdentifier, EquipmentType
from mrcs_core.data.json import JSONable, JSONify
from mrcs_core.equipment.control_router.control_router_conf import ControlRouterConf
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import PublicationRoutingKey, SubscriptionRoutingKey


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
        return EquipmentIdentifier(EquipmentType.CRT, None, 1)


    @classmethod
    def subscription_routing_keys(cls):
        return (SubscriptionRoutingKey(EquipmentFilter.any(), cls.id()),)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: NodeTopology.ServiceConfiguration, conf: ControlRouterConf):
        super().__init__(ops, MQTopology.SINGLE)
        self.__conf = conf

        self.__station = None
        self.__monitor_task = None
        self.__station_ready = False
        self.__station_ready_event = asyncio.Event()


    # ----------------------------------------------------------------------------------------------------------------
    # messaging handlers...

    def handle_startup(self):
        self.logger.debug('handle_startup')
        if self.__monitor_task is None:
            self.__monitor_task = self.async_loop.create_task(self.monitor())


    async def handle_message(self, message: Message):
        self.logger.info(f'handle_message:{JSONify.as_jdict(message)}')

        await self.__wait_until_station_ready()

        try:
            command = Command.construct_from_jdict(message.body)
            await self.station.send_command(command)
        except Exception as exc:
            self.logger.warning(f'handle_message:{type(exc).__name__}:{exc} on:{message}')
            raise


    async def __wait_until_station_ready(self):
        await self.__station_ready_event.wait()


    def run(self, *args):
        self.logger.debug('run')
        # TODO: db table management here
        super().run()


    # ----------------------------------------------------------------------------------------------------------------
    # control router handlers...

    def on_dataset(self, report: JSONable):
        self.logger.info(f'on_dataset:{report}')

        source = ControlRouterIdentity.get(report)
        routing_key = PublicationRoutingKey(source, EquipmentFilter.any())

        outgoing = Message(routing_key, report)
        self.async_loop.create_task(self.mq_client.publish(outgoing))


    def on_connection_lost(self):
        self.station_ready = False
        self.logger.warning('on_connection_lost')


    # ----------------------------------------------------------------------------------------------------------------

    async def monitor(self):
        self.logger.debug('monitor')

        while True:
            try:
                self.__station = await Station.connect(self.conf, self.on_dataset, self.on_connection_lost)

                await self.station.set_broadcast_flags(self.conf.subscription)
                await self.station.get_system_state()
                self.station_ready = True

                while True:
                    await asyncio.sleep(self.__KEEP_ALIVE_INTERVAL)
                    await self.station.get_system_state()

            except ConnectionError as exc:
                self.logger.warning(f'connection error:{exc}')
                self.station_ready = False
                await asyncio.sleep(self.__RETRY_INTERVAL)

            except asyncio.CancelledError:
                self.logger.warning('monitor cancelled')
                raise

            except Exception as exc:
                self.station_ready = False
                self.logger.warning(f'monitor exception: {type(exc).__name__}: {exc}')
                await asyncio.sleep(5)

            finally:
                self.station_ready = False
                if self.station is not None:
                    await self.station.close()
                    self.__station = None


    async def halt(self):
        self.logger.debug('halt')

        await self.shutdown()
        await super().halt()


    async def shutdown(self):
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


    def close(self):
        self.logger.debug('close')

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
        return (f'ControlRouterNode:{{conf:{self.conf}, station:{self.station}, station_ready:{self.station_ready}, '
                f'ops:{self.ops}, mq_client:{self.mq_client}}}')
