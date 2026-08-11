"""
Created on 6 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

Z21 control router station

Classes in support of the Rocco Z21 DCC control router station:
https://www.z21.eu/en/products/z21

Based on code:
https://github.com/botmonster/z21aio/tree/main
https://gitlab.com/z21-fpm/z21_python
"""

import asyncio
import errno
from asyncio import DatagramTransport
from typing import Any, Callable, Self

from mrcs_control.dcc.z21.command.broadcast import Broadcast
from mrcs_control.dcc.z21.command.command import Command
from mrcs_control.dcc.z21.command.dataset import Dataset
from mrcs_control.dcc.z21.command.header import Header
from mrcs_control.dcc.z21.command.protocol import Protocol
from mrcs_control.dcc.z21.equipment.equpiment_report import EquipmentReport
from mrcs_core.equipment.control_router.control_router_conf import ControlRouterConf
from mrcs_core.equipment.control_router.control_router_subscription import ControlRouterSubscription
from mrcs_core.sys.ipv4_address import IPv4Address
from mrcs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

class Station(object):
    """
    Z21 control router station
    """

    DEFAULT_IP_ADDRESS = IPv4Address.construct('192.168.1.111')
    DEFAULT_PORT = 21105
    DEFAULT_TIMEOUT = 2.0
    DEFAULT_SUBSCRIPTION = ControlRouterSubscription(Broadcast.CAN_DETECTOR, Broadcast.RAILCOM_DATA_ALL,
                                                     Broadcast.TRACK, Broadcast.X_LOCO_INFO_ALL)
    __DEFAULT_TIME_BETWEEN_SENDS = 0.1


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, conf: ControlRouterConf, on_response: Callable, on_connection_lost: Callable):
        self.__conf = conf
        self.__on_response = on_response
        self.__on_connection_lost = on_connection_lost

        self.__transport: DatagramTransport | None = None
        self.__protocol: Protocol | None = None
        self.__has_connection = False
        self.__response_event = asyncio.Event()

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

    async def connect(self) -> None:
        loop = asyncio.get_running_loop()

        try:
            # Binding without SO_REUSEPORT makes the client endpoint exclusive:
            # a second MRCS Z21 client cannot silently share this port.
            transport, protocol = await loop.create_datagram_endpoint(
                lambda: Protocol(self.station_dataset_handler, self.station_connection_lost_handler),
                local_addr=('0.0.0.0', self.conf.port),
                remote_addr=(self.conf.ip_address.dot_decimal, self.conf.port),
            )

        except OSError as exc:
            if exc.errno == errno.EADDRINUSE:
                raise RuntimeError(
                    f'Z21 client UDP port {self.conf.port} is already in use; '
                    'stop the other MRCS Z21 client before starting this utility.') from exc
            raise

        # TODO: use conf.timeout? Do we need receive_packet() if broadcast is off?
        # https://github.com/botmonster/z21aio/blob/a615edc27021955ed3bfebc79568c5fffc89c7ac/src/z21aio/station.py#L309

        self.__transport = transport
        self.__protocol = protocol
        self.__has_connection = True

        self.logger.debug(f'connected:{transport.get_extra_info("sockname")}')


    def station_dataset_handler(self, dataset: Dataset) -> None:
        self.logger.debug(f'station_dataset_handler:{dataset}')

        if dataset.header == Header.LAN_SYSTEMSTATE_DATACHANGED:
            self.__response_event.set()

        try:
            self.on_response(EquipmentReport.construct_from_dataset(dataset))

        except TypeError:
            self.logger.warning(f'dataset_handler unsupported: {dataset}')


    def station_connection_lost_handler(self) -> None:
        if not self.__has_connection:
            return

        self.__has_connection = False
        self.logger.warning('station_connection_lost_handler')
        self.on_connection_lost()


    # ----------------------------------------------------------------------------------------------------------------

    async def set_broadcast_flags(self, subscription: ControlRouterSubscription | None = None) -> None:
        self.logger.debug('set_broadcast_flags')

        subscription = self.conf.subscription if subscription is None else subscription
        command = Command.construct(Header.LAN_SET_BROADCAST_FLAGS, subscription.value)

        await self.send_command(command)


    async def get_system_state(self, timeout: float = DEFAULT_TIMEOUT) -> None:
        self.logger.debug('set_broadcast_flags')

        self.__response_event.clear()

        command = Command.construct(Header.LAN_SYSTEMSTATE_GETDATA)
        await self.send_command(command)

        try:
            await asyncio.wait_for(self.__response_event.wait(), timeout)
        except asyncio.TimeoutError as exc:
            self.station_connection_lost_handler()
            raise ConnectionError('Z21 control router did not respond') from exc


    async def logout(self) -> None:
        self.logger.debug('logout')

        command = Command.construct(Header.LAN_LOGOFF)
        await self.send_command(command)


    # ----------------------------------------------------------------------------------------------------------------

    async def send_command(self, command: Command) -> None:
        if self.__transport is None:
            raise ConnectionError('not connected to a Z21 station')

        chars = command.dataset.as_bytes()
        self.logger.debug(f'send_command:{chars.hex(" ")}')

        self.__transport.sendto(command.dataset.as_bytes())
        await asyncio.sleep(self.__DEFAULT_TIME_BETWEEN_SENDS)


    async def close(self) -> None:
        self.logger.debug('close')

        if self.__transport is None:
            return

        self.__has_connection = False

        try:
            await self.logout()
        except (OSError, ConnectionError) as exc:
            self.logger.warning(f'send_command:{exc}')

        if self.__transport is not None:
            self.__transport.close()
            self.__transport = None


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

        return (f'Station:{{conf:{self.conf}, on_response:{on_response}, '
                f'on_connection_lost:{on_connection_lost}, has_connection:{self.has_connection}, '
                f'transport:{bool(self.__transport)}, protocol:{self.__protocol}}}')
