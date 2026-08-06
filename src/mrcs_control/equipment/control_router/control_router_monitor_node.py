"""
Created on 31 Jul 2026

@author: Bruno Beloff (bbeloff@me.com)

An AsyncPublisherNode that implements an interface between a Z21 control router and the messaging system.
This version of the interface is for monitoring only - commands cannot be sent to the control router.

Test with:
mrcs_control_router -t -r -v
"""

import asyncio

from mrcs_control.dcc.z21.command.station import Z21Station
from mrcs_control.equipment.control_router.control_router import CRT
from mrcs_control.operations.async_messaging_node import AsyncPublisherNode
from mrcs_control.operations.node_enums import NodeTopology
from mrcs_core.data.equipment_identity import EquipmentFilter, EquipmentIdentifier, EquipmentType
from mrcs_core.data.json import JSONable
from mrcs_core.equipment.control_router.control_router_conf import ControlRouterConf
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import PublicationRoutingKey


# TODO: periodically read the control router system state (as the keep-alive) and save to db table.

# --------------------------------------------------------------------------------------------------------------------

class ControlRouterMonitorNode(AsyncPublisherNode):
    """
    raises events
    """


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def id(cls):
        return EquipmentIdentifier(EquipmentType.CRT, None, CRT.Monitor)


    @classmethod
    def publication_routing_key(cls):
        return PublicationRoutingKey(cls.id(), EquipmentFilter.any())


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: NodeTopology.ServiceConfiguration, conf: ControlRouterConf):
        super().__init__(ops)
        self.__conf = conf
        self.__monitor_task = None


    # ----------------------------------------------------------------------------------------------------------------

    def handle_startup(self):
        self.logger.debug('ControlRouterMonitorNode - handle_startup')
        self.__monitor_task = self.async_loop.create_task(self.monitor())


    async def monitor(self):
        self.logger.debug('ControlRouterMonitorNode - monitor')

        station = None

        try:
            station = await Z21Station.connect(self.conf, self.on_dataset, self.on_connection_lost)
            self.logger.debug(f'ControlRouterMonitorNode - monitor - station: {station}')

            await station.set_broadcast_flags(self.conf.subscription)

            while True:
                await asyncio.sleep(1)  # TODO: test connection here?

        except asyncio.CancelledError:
            self.logger.info('monitor cancelled')
            raise

        except Exception as exc:
            self.logger.exception(f'monitor failed: {exc}')
            self.async_loop.stop()
            raise

        finally:
            if station is not None:
                await station.close()


    async def halt(self):
        self.logger.debug('ControlRouterMonitorNode - halt')

        await self.shutdown()
        await super().halt()


    async def shutdown(self):
        self.logger.debug('ControlRouterMonitorNode - shutdown')

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
        self.logger.debug('ControlRouterMonitorNode - close')

        if self.async_loop is None or self.async_loop.is_running():
            # If the node is running, shutdown must be awaited by the loop.
            if self.async_loop is not None:
                self.async_loop.create_task(self.shutdown())
            return

        self.async_loop.run_until_complete(self.shutdown())
        self.logger.debug('closed')


    # ----------------------------------------------------------------------------------------------------------------

    def on_dataset(self, report: JSONable):
        self.logger.info(f'publishing: {report}')

        outgoing = Message(self.publication_routing_key(), report)
        self.async_loop.create_task(self.mq_client.publish(outgoing))


    def on_connection_lost(self, exc: Exception):
        self.logger.warning(f'connection lost - exc: {exc}')


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def conf(self):
        return self.__conf


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'ControlRouterMonitorNode:{{conf:{self.conf}, ops:{self.ops}, mq_client:{self.mq_client}}}'
