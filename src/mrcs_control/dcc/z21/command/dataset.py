"""
Created on 5 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

The unit of Z21 communication

Classes in support of the Rocco Z21 DCC command station:
https://www.z21.eu/en/products/z21

Based on code:
https://github.com/botmonster/z21aio/tree/main
https://gitlab.com/z21-fpm/z21_python
"""

import struct
from functools import reduce

from mrcs_control.dcc.z21.command.header import Header, XHeader


# --------------------------------------------------------------------------------------------------------------------

class Dataset(object):
    """
    The unit of Z21 LAN communication
    """


    @classmethod
    def construct_from_bytes(cls, chars: bytes) -> Dataset | XBusDataset:
        if len(chars) < 4:
            raise ValueError(f'Dataset requires at least 4 bytes, got:{chars.hex(" ")}')

        total_len, header_int = struct.unpack("<HH", chars[:4])

        if len(chars) != total_len:
            raise ValueError(f'Dataset length does not match header, specified:{total_len} got:{chars.hex(" ")}')

        header = Header.construct(header_int)
        data = chars[4:total_len]

        return XBusDataset.construct(header, data) if header == Header.LAN_X else Dataset(header, data)


    @classmethod
    def construct_from_int(cls, header: Header, int_value: int):
        return Dataset(header, struct.pack("<I", int_value))


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, header: Header, data: bytes = b''):
        self.__header = header
        self.__data = data


    def __eq__(self, other):
        try:
            return self.header == other.header and self.x_header == other.x_header and self.data == other.data
        except (AttributeError, TypeError):
            return False


    # ----------------------------------------------------------------------------------------------------------------

    def as_bytes(self):
        return struct.pack("<HH", self.total_len, self.header) + self.data


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def header(self):
        return self.__header


    @property
    def x_header(self):
        return None


    @property
    def data(self):
        return self.__data


    @property
    def total_len(self):
        return len(self.data) + 4


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'Dataset:{{header:0x{self.header.value:04x} [{self.header.name}], total_len:{self.total_len}, '
                f'data:{self.data.hex(" ")}}}')


# --------------------------------------------------------------------------------------------------------------------

class XBusDataset(Dataset):
    """
    The unit of Z21 XLAN communication
    """


    @classmethod
    def construct(cls, header: Header, data: bytes):
        if len(data) < 1:
            raise ValueError(f'XBusDataset data length must be at least 1 byte')

        x_header = XHeader.construct(data[0])
        dataset = XBusDataset(header, x_header, data[1:-1], data[-1])

        if dataset.calculated_xor != dataset.xor:
            raise ValueError(f'XBusDataset calculated xor {dataset.calculated_xor:02x} '
                             f'does not match supplied xor {dataset.xor:02x}')

        return dataset


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, header: Header, x_header: XHeader, data: bytes, xor: int):
        super().__init__(header, data)

        self.__x_header = x_header
        self.__xor = xor


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def calculated_xor(self) -> int:
        return reduce(lambda acc, x: acc ^ x, self.data, self.x_header)


    @property
    def xor(self):
        return self.__xor


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def x_header(self):
        return self.__x_header


    @property
    def total_len(self):
        return len(self.data) + 6


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'XBusDataset:{{header:0x{self.header.value:04x} [{self.header.name}], '
                f'x_header:0x{self.x_header.value:04x} [{self.x_header.name}], total_len:{self.total_len}, '
                f'data:{self.data.hex(" ")}, xor:0x{self.xor:02x}}}')
