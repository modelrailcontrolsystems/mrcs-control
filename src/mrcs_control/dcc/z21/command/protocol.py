"""
Created on 6 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

Z21 communications handler

Classes in support of the Rocco Z21 DCC command station:
https://www.z21.eu/en/products/z21

Based on code:
https://github.com/botmonster/z21aio/tree/main
https://gitlab.com/z21-fpm/z21_python
"""

import struct
from asyncio import DatagramProtocol
from typing import Callable

from mrcs_control.dcc.z21.command.dataset import Dataset
from mrcs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

class Z21Protocol(DatagramProtocol):
    """
    Z21 communications handler
    """


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, dataset_handler: Callable[[Dataset], None],
                 connection_lost_handler: Callable[[Exception | None], None]):
        self.__dataset_handler = dataset_handler
        self.__connection_lost_handler = connection_lost_handler

        self.__logger = Logging.getLogger()


    # ----------------------------------------------------------------------------------------------------------------

    def connection_made(self, transport):
        pass


    def connection_lost(self, exc):
        self.__connection_lost_handler(exc)


    def datagram_received(self, data: bytes, addr: tuple[str, int]):
        offset = 0
        while offset < len(data):
            try:
                dataset = Dataset.construct_from_bytes(data[offset:])
                self.__dataset_handler(dataset)
                offset += dataset.total_len

            except (ValueError, struct.error) as exc:
                self.logger.error('datagram_received on %s at offset %d: %s <%s>', addr, offset, exc,
                                  data[offset:].hex(' '))
                return


    def error_received(self, exc):
        self.logger.warn(f'error_received - exc:{exc}')


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def logger(self):
        return self.__logger


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        dataset_handler = None if self.__dataset_handler is None else self.__dataset_handler.__name__
        connection_lost_handler = None if self.__connection_lost_handler is None \
            else self.__connection_lost_handler.__name__

        return (f'Z21Protocol:{{dataset_handler:{dataset_handler}, '
                f'connection_lost_handler:{connection_lost_handler}}}')
