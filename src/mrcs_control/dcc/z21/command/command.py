"""
Created on 26 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

A mapping between Rocco Z21 DCC commands and their report_types

Classes in support of the Rocco Z21 DCC command station:
https://www.z21.eu/en/products/z21
"""

import struct
from collections import OrderedDict

from mrcs_control.dcc.z21.command import XCommandMetadata
from mrcs_control.dcc.z21.command.command_metadata import CommandMetadata
from mrcs_control.dcc.z21.command.dataset import Dataset, XDataset
from mrcs_control.dcc.z21.command.header import Header, XHeader
from mrcs_core.data.json import JSONable


# --------------------------------------------------------------------------------------------------------------------

class Command(JSONable):
    """
    An enumeration of all the supported commands
    """


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def construct(cls, header: Header, *args):
        if not CommandMetadata.is_supported(header):
            raise TypeError(f'unsupported header: {header}')

        return cls(header, *args)


    @classmethod
    def construct_from_jdict(cls, jdict):
        if not jdict:
            return None

        type_name = jdict.get('type')

        if type_name == XCommand.type_name():
            return XCommand.construct_from_jdict(jdict)

        if type_name != cls.type_name():
            raise TypeError(f'required type:{cls.type_name()} got:{type_name}')

        # may raise KeyError
        header = Header[jdict['header']]
        args = jdict.get('args')

        return cls(header, *args)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, header: Header, *args: int):
        self._header = header
        self._args = args


    def __eq__(self, other):
        try:
            return self.header == other.header and self.args == other.args
        except (AttributeError, TypeError):
            return False


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def dataset(self) -> Dataset:
        data = b''  # TODO: implement properly
        return Dataset(self.header, data)


    @property
    def data_format(self):
        return CommandMetadata.find(self.header).data_format


    @property
    def report_type(self):
        return CommandMetadata.find(self.header).report_type


    # ----------------------------------------------------------------------------------------------------------------

    def as_json(self, **kwargs):
        jdict = OrderedDict()

        jdict['type'] = self.type_name()

        jdict['header'] = self.header.name
        jdict['args'] = self.args

        return jdict


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def header(self):
        return self._header


    @property
    def args(self):
        return self._args


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'Command:{{header:{self.header.name}, args:{self.args}}}'


# --------------------------------------------------------------------------------------------------------------------

class XCommand(Command):
    """
    An enumeration of all the supported commands
    """


    @classmethod
    def construct(cls, x_header: XHeader, *args: int):
        if not XCommandMetadata.is_supported(x_header):
            raise TypeError(f'unsupported x_header: {x_header}')

        return cls(x_header, *args)


    @classmethod
    def construct_from_jdict(cls, jdict):
        if not jdict:
            return None

        type_name = jdict.get('type')

        if type_name != cls.type_name():
            raise TypeError(f'required type:{cls.type_name()} got:{type_name}')

        # may raise KeyError
        x_header = XHeader[jdict['x_header']]
        args = jdict.get('args')

        return cls(x_header, *args)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, x_header: XHeader, *args):
        super().__init__(Header.LAN_X, *args)
        self.__x_header = x_header


    def __eq__(self, other):
        try:
            return self.header == other.header and self.x_header == other.x_header and self.args == other.args
        except (AttributeError, TypeError):
            return False


    # ----------------------------------------------------------------------------------------------------------------

    def as_json(self, **kwargs):
        jdict = OrderedDict()

        jdict['type'] = self.type_name()

        jdict['x_header'] = self.x_header.name
        jdict['args'] = self.args

        return jdict


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def dataset(self) -> XDataset:
        data = struct.pack('<' + self.data_format, *self.args)
        return XDataset.construct_from_command(self.header, self.x_header, data)


    @property
    def data_format(self):
        return XCommandMetadata.find(self.x_header).data_format


    @property
    def report_type(self):
        return XCommandMetadata.find(self.x_header).report_type


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def x_header(self):
        return self.__x_header


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'XCommand:{{header:{self.header.name}, x_header:{self.x_header.name}, '
                f'args:{[int(arg) for arg in self.args]}}}')
