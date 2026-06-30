"""
Created on 6 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

Z21 command station

Classes in support of the Rocco Z21 DCC command station:
https://www.z21.eu/en/products/z21

Based on code:
https://github.com/botmonster/z21aio/tree/main
https://gitlab.com/z21-fpm/z21_python
"""

import asyncio
from asyncio import CancelledError, DatagramTransport
from typing import Any, Callable, Self

from mrcs_control.dcc.z21.command.broadcast import Broadcast
from mrcs_control.dcc.z21.command.command import Command
from mrcs_control.dcc.z21.command.dataset import Dataset
from mrcs_control.dcc.z21.command.header import Header
from mrcs_control.dcc.z21.command.protocol import Z21Protocol
from mrcs_control.dcc.z21.equipment.z21_equpiment_report import Z21EquipmentReport
from mrcs_core.equipment.control_router.control_router_conf import ControlRouterConf
from mrcs_core.equipment.control_router.control_router_subscription import ControlRouterSubscription
from mrcs_core.sys.ipv4_address import IPv4Address
from mrcs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

class Z21Station(object):
    """
    Z21 command station
    """

    DEFAULT_IP_ADDRESS = IPv4Address.construct('192.168.1.111')
    DEFAULT_PORT = 21105
    DEFAULT_TIMEOUT = 2.0
    DEFAULT_SUBSCRIPTION = ControlRouterSubscription(Broadcast.CAN_DETECTOR, Broadcast.RAILCOM_DATA_ALL,
                                                     Broadcast.TRACK, Broadcast.X_LOCO_INFO_ALL)
    __KEEP_ALIVE_INTERVAL = 30.0


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    async def connect(cls, conf: ControlRouterConf, on_response: Callable, on_connection_lost: Callable) -> Z21Station:
        loop = asyncio.get_running_loop()

        station = cls(conf, on_response, on_connection_lost)

        transport, protocol = await loop.create_datagram_endpoint(
            lambda: Z21Protocol(station.dataset_handler, station.connection_lost_handler),
            remote_addr=(conf.ip_address, conf.port),
        )

        # TODO: use conf.timeout? Do we need receive_packet() if broadcast is off?
        # https://github.com/botmonster/z21aio/blob/a615edc27021955ed3bfebc79568c5fffc89c7ac/src/z21aio/station.py#L309

        station.__transport = transport
        station.__protocol = protocol
        station.__has_connection = True

        station.__keep_alive_task = asyncio.create_task(station.__keep_alive_loop())

        return station


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, conf: ControlRouterConf, on_response: Callable, on_connection_lost: Callable):
        self.__conf = conf
        self.__on_response = on_response
        self.__on_connection_lost = on_connection_lost

        self.__transport: DatagramTransport | None = None
        self.__protocol: Z21Protocol | None = None
        self.__has_connection = False

        self.__keep_alive_task: asyncio.Task[None] | None = None

        self.__logger = Logging.getLogger()


    async def __aenter__(self) -> Self:
        return self


    async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: Any,
    ) -> None:
        await self.close()


    # ----------------------------------------------------------------------------------------------------------------

    def dataset_handler(self, dataset: Dataset) -> None:
        try:
            self.on_response(Z21EquipmentReport.construct_from_dataset(dataset))

        except TypeError:
            self.logger.warning(f'dataset_handler unsupported: {dataset}')


    def connection_lost_handler(self, ex: Exception | None) -> None:
        self.logger.debug(f'connection_lost_handler - ex:{ex}')
        self.on_connection_lost(ex)


    # ----------------------------------------------------------------------------------------------------------------

    async def set_broadcast_flags(self, subscription: ControlRouterSubscription | None = None) -> None:
        subscription = self.conf.subscription if subscription is None else subscription
        command = Command.construct(Header.LAN_SET_BROADCAST_FLAGS, subscription.value)

        await self.send_command(command)


    async def get_system_state(self) -> None:
        command = Command.construct(Header.LAN_SYSTEMSTATE_GETDATA)
        await self.send_command(command)


    async def logout(self) -> None:
        command = Command.construct(Header.LAN_LOGOFF)
        await self.send_command(command)


    # ----------------------------------------------------------------------------------------------------------------

    async def send_command(self, command: Command) -> None:
        self.logger.debug(f'*** station - send_command:{command}')

        if self.__transport is None:
            raise ConnectionError('not connected to a Z21 station')

        self.__transport.sendto(command.dataset.as_bytes())


    async def close(self) -> None:
        self.__has_connection = False

        if self.__keep_alive_task is not None:
            self.__keep_alive_task.cancel()
            try:
                await self.__keep_alive_task
            except asyncio.CancelledError as ex:
                self.logger.warning(f'error while canceling keep alive task:{ex}')

        try:
            await self.logout()
        except (OSError, ConnectionError) as ex:
            self.logger.warning(f'error while logging out:{ex}')

        if self.__transport is not None:
            self.__transport.close()


    # ----------------------------------------------------------------------------------------------------------------

    async def __keep_alive_loop(self) -> None:
        while self.has_connection:
            try:
                await asyncio.sleep(self.__KEEP_ALIVE_INTERVAL)
                if self.has_connection:
                    await self.set_broadcast_flags()
            except CancelledError:
                break

            except (OSError, ConnectionError) as ex:
                self.logger.debug(f'keep-alive failed: {ex}')


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def conf(self):
        return self.__conf


    @property
    def on_response(self):
        return self.__on_response


    @property
    def on_connection_lost(self):
        return self.__on_connection_lost


    @property
    def has_connection(self):
        return self.__has_connection


    @property
    def logger(self):
        return self.__logger


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'Z21Station:{{conf:{self.conf}, on_response:{self.on_response}, '
                f'on_connection_lost:{self.on_connection_lost}, has_connection:{self.has_connection}, '
                f'transport:{bool(self.__transport)}, protocol:{self.__protocol}}}')
