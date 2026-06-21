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
from mrcs_control.dcc.z21.command.dataset import Dataset
from mrcs_control.dcc.z21.command.header import Header
from mrcs_control.dcc.z21.command.protocol import Z21Protocol
from mrcs_control.dcc.z21.equipment.z21_equpiment_report import Z21EquipmentReport
from mrcs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

class Z21Station(object):
    """
    Z21 command station
    """

    __DEFAULT_PORT = 21105
    __DEFAULT_TIMEOUT = 2.0
    __BROADCAST_SUBSCRIPTIONS = (
            Broadcast.TRACK | Broadcast.CAN_DETECTOR | Broadcast.X_LOCO_INFO_ALL | Broadcast.RAILCOM_DATA_ALL)
    # Broadcast.LOCONET_OCCUPANCY
    __KEEP_ALIVE_INTERVAL = 30.0


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    async def connect(cls, on_dataset: Callable, on_connection_lost: Callable, host: str, port: int = __DEFAULT_PORT,
                      timeout: float = __DEFAULT_TIMEOUT, keep_alive: bool = True) -> Z21Station:
        loop = asyncio.get_running_loop()

        station = cls(on_dataset, on_connection_lost, host, port, timeout, cls.__BROADCAST_SUBSCRIPTIONS)

        transport, protocol = await loop.create_datagram_endpoint(
            lambda: Z21Protocol(station.dataset_handler, station.connection_lost_handler),
            remote_addr=(station.host, station.port),
        )

        station.__transport = transport
        station.__protocol = protocol
        station.__has_connection = True

        if keep_alive:
            station.__keep_alive_task = asyncio.create_task(station.__keep_alive_loop())

        await station.set_broadcast_flags()

        return station


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, on_dataset: Callable, on_connection_lost: Callable, host: str, port: int,
                 timeout: float, subscriptions: int):
        self.__on_dataset = on_dataset
        self.__on_connection_lost = on_connection_lost

        self.__host = host
        self.__port = port
        self.__timeout = timeout
        self.__subscriptions = subscriptions

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
            obj = Z21EquipmentReport.construct_from_dataset(dataset)
            self.on_dataset(obj)

        except TypeError:
            self.logger.warning(f'dataset_handler unsupported: {dataset}')


    def connection_lost_handler(self, ex: Exception | None) -> None:
        self.logger.debug(f'connection_lost_handler - ex:{ex}')
        self.on_connection_lost(ex)


    # ----------------------------------------------------------------------------------------------------------------

    async def set_broadcast_flags(self) -> None:
        dataset = Dataset.construct_from_int(Header.LAN_SET_BROADCAST_FLAGS, self.subscriptions)
        await self.send_dataset(dataset)


    async def get_system_state(self) -> None:
        dataset = Dataset.construct_from_int(Header.LAN_SYSTEMSTATE_GETDATA, self.subscriptions)
        await self.send_dataset(dataset)


    async def logout(self) -> None:
        dataset = Dataset(Header.LAN_LOGOFF)
        await self.send_dataset(dataset)


    async def send_dataset(self, dataset: Dataset) -> None:
        self.logger.debug(f'send_dataset:{dataset}')

        if self.__transport is None:
            raise ConnectionError('not connected to a Z21 station')

        self.__transport.sendto(dataset.as_bytes())


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
    def on_dataset(self):
        return self.__on_dataset


    @property
    def on_connection_lost(self):
        return self.__on_connection_lost


    @property
    def host(self):
        return self.__host


    @property
    def port(self):
        return self.__port


    @property
    def timeout(self):
        return self.__timeout


    @property
    def subscriptions(self):
        return self.__subscriptions


    @property
    def has_connection(self):
        return self.__has_connection


    @property
    def logger(self):
        return self.__logger


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (
            f'Z21Station:{{on_dataset:{self.on_dataset}, on_connection_lost:{self.on_connection_lost}, '
            f'host:{self.host}, port:{self.port}, timeout:{self.timeout}, '
            f'subscriptions:0x{self.subscriptions:08x}, has_connection:{self.has_connection}, '
            f'transport:{bool(self.__transport)}, protocol:{self.__protocol}}}')
