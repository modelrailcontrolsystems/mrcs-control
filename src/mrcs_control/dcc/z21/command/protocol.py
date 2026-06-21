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
        self.logger.debug('connection_made')


    def connection_lost(self, ex):
        self.logger.debug(f'connection_lost - ex:{ex}')
        self.__connection_lost_handler(ex)


    def datagram_received(self, chars: bytes, addr: tuple[str, int]):
        # self.logger.debug(f'datagram_received - chars:{chars.hex(" ")}')

        offset = 0
        while offset < len(chars):
            try:
                dataset = Dataset.construct_from_bytes(chars[offset:])
                self.__dataset_handler(dataset)
                offset += dataset.total_len

            except (ValueError, struct.error) as ex:
                self.logger.error('datagram_received on %s at offset %d: %s <%s>', addr, offset, ex,
                                  chars[offset:].hex(' '))
                return


    def error_received(self, ex):
        self.logger.warn(f'error_received - ex:{ex}')


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def logger(self):
        return self.__logger


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'Z21Protocol:{{dataset_handler:{bool(self.__dataset_handler)}, '
                f'connection_lost_handler:{bool(self.__connection_lost_handler)}}}')
