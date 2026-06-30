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
    def construct_from_bytes(cls, chars: bytes) -> Dataset | XDataset:
        if len(chars) < 4:
            raise ValueError(f'Dataset requires at least 4 bytes, got:{chars.hex(" ")}')

        total_len, header_int = struct.unpack('<HH', chars[:4])

        if len(chars) != total_len:
            raise ValueError(f'Dataset length does not match header, specified:{total_len} got:{chars.hex(" ")}')

        header = Header.construct(header_int)
        data = chars[4:total_len]

        return XDataset.construct_from_response(header, data) if header == Header.LAN_X else Dataset(header, data)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, header: Header, data: bytes = b''):
        self._header = header
        self._data = data


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
        return self._header


    @property
    def x_header(self):
        return None


    @property
    def data(self):
        return self._data


    @property
    def total_len(self):
        return len(self.data) + 4


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'Dataset:{{header:0x{self.header.value:04x} [{self.header.name}], total_len:{self.total_len}, '
                f'data:{self.data.hex(" ")}}}')


# --------------------------------------------------------------------------------------------------------------------

class XDataset(Dataset):
    """
    The unit of Z21 XLAN communication
    """


    @staticmethod
    def calculated_xor(x_header, data, ) -> int:
        return reduce(lambda acc, x: acc ^ x, data, x_header)


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def construct_from_command(cls, header: Header, x_header: XHeader, data: bytes):
        xor = cls.calculated_xor(x_header, data)
        return XDataset(header, x_header, data, xor)


    @classmethod
    def construct_from_response(cls, header: Header, data: bytes):
        if len(data) < 1:
            raise ValueError(f'XDataset data length must be at least 1 byte')

        x_header = XHeader.construct(data[0])
        dataset = XDataset(header, x_header, data[1:-1], data[-1])
        calculated_xor = cls.calculated_xor(dataset.x_header, dataset.data)

        if calculated_xor != dataset.xor:
            raise ValueError(f'XDataset calculated xor {calculated_xor:02x} '
                             f'does not match supplied xor {dataset.xor:02x}')

        return dataset


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, header: Header, x_header: XHeader, data: bytes, xor: int):
        super().__init__(header, data)

        self.__x_header = x_header
        self.__xor = xor


    # ----------------------------------------------------------------------------------------------------------------

    def as_bytes(self):
        return struct.pack('<HHB', self.total_len, self.header, self.x_header) + self.data + bytes([self.xor])


    # ----------------------------------------------------------------------------------------------------------------

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
        return (f'XDataset:{{header:0x{self.header.value:04x} [{self.header.name}], '
                f'x_header:0x{self.x_header.value:04x} [{self.x_header.name}], total_len:{self.total_len}, '
                f'data:{self.data.hex(" ")}, xor:0x{self.xor:02x}}}')
