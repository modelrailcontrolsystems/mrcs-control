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
import errno
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
    # The Z21 associates broadcast delivery with the client's UDP endpoint.
    # Keep this port stable across process restarts instead of allowing the OS
    # to allocate a new ephemeral source port each time.
    DEFAULT_CLIENT_PORT = 21106
    DEFAULT_TIMEOUT = 2.0
    DEFAULT_SUBSCRIPTION = ControlRouterSubscription(Broadcast.CAN_DETECTOR, Broadcast.RAILCOM_DATA_ALL,
                                                     Broadcast.TRACK, Broadcast.X_LOCO_INFO_ALL)
    __DEFAULT_TIME_BETWEEN_SENDS = 0.1
    __KEEP_ALIVE_INTERVAL = 30.0


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    async def connect(cls, conf: ControlRouterConf, on_response: Callable, on_connection_lost: Callable) -> Z21Station:
        loop = asyncio.get_running_loop()

        station = cls(conf, on_response, on_connection_lost)

        try:
            # Binding without SO_REUSEPORT makes the client endpoint exclusive:
            # a second MRCS Z21 client cannot silently share this port.
            transport, protocol = await loop.create_datagram_endpoint(
                lambda: Z21Protocol(station.station_dataset_handler, station.station_connection_lost_handler),
                local_addr=('0.0.0.0', conf.port),
                remote_addr=(conf.ip_address.dot_decimal, conf.port),
            )

        except OSError as exc:
            if exc.errno == errno.EADDRINUSE:
                raise RuntimeError(
                    f'Z21 client UDP port {cls.DEFAULT_CLIENT_PORT} is already in use; '
                    'stop the other MRCS Z21 client before starting this utility.') from exc
            raise

        # TODO: use conf.timeout? Do we need receive_packet() if broadcast is off?
        # https://github.com/botmonster/z21aio/blob/a615edc27021955ed3bfebc79568c5fffc89c7ac/src/z21aio/station.py#L309

        station.__transport = transport
        station.__protocol = protocol
        station.__has_connection = True

        station.logger.debug(f'connected - local:{transport.get_extra_info("sockname")}')

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

    def station_dataset_handler(self, dataset: Dataset) -> None:
        self.logger.debug(f'station_dataset_handler:{dataset}')
        try:
            self.on_response(Z21EquipmentReport.construct_from_dataset(dataset))

        except TypeError:
            self.logger.warning(f'dataset_handler unsupported: {dataset}')


    def station_connection_lost_handler(self, exc: Exception | None) -> None:
        self.on_connection_lost(exc)


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
        if self.__transport is None:
            raise ConnectionError('not connected to a Z21 station')

        chars = command.dataset.as_bytes()
        self.logger.info(f'*** station - send_command:{chars.hex(" ")}')

        self.__transport.sendto(command.dataset.as_bytes())
        await asyncio.sleep(self.__DEFAULT_TIME_BETWEEN_SENDS)


    async def close(self) -> None:
        self.__has_connection = False

        if self.__keep_alive_task is not None:
            self.__keep_alive_task.cancel()
            try:
                await self.__keep_alive_task
            except asyncio.CancelledError as exc:
                self.logger.warning(f'error while canceling keep alive task:{exc}')

        try:
            await self.logout()
        except (OSError, ConnectionError) as exc:
            self.logger.warning(f'error while logging out:{exc}')

        if self.__transport is not None:
            self.__transport.close()


    # ----------------------------------------------------------------------------------------------------------------

    async def __keep_alive_loop(self) -> None:  # TODO: move to control monitor node
        while self.has_connection:
            try:
                await asyncio.sleep(self.__KEEP_ALIVE_INTERVAL)
                if self.has_connection:
                    await self.set_broadcast_flags()  # TODO: change this to get system state
            except CancelledError:
                break

            except (OSError, ConnectionError) as exc:
                self.logger.debug(f'keep-alive failed: {exc}')


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
        on_response = None if self.__on_response is None else self.__on_response.__name__
        on_connection_lost = None if self.__on_connection_lost is None else self.__on_connection_lost.__name__

        return (f'Z21Station:{{conf:{self.conf}, on_response:{on_response}, '
                f'on_connection_lost:{on_connection_lost}, has_connection:{self.has_connection}, '
                f'transport:{bool(self.__transport)}, protocol:{self.__protocol}}}')
