"""
Created on 26 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

An abstraction over Rocco Z21 DCC command datasets

Classes in support of the Rocco Z21 DCC control router station:
https://www.z21.eu/en/products/z21
"""

import struct
from collections import OrderedDict
from typing import Any

from mrcs_control.dcc.z21.command.command_metadata import CommandMetadata, XCommandMetadata
from mrcs_control.dcc.z21.command.dataset import Dataset, XDataset
from mrcs_control.dcc.z21.command.header import Header, XHeader
from mrcs_core.data.json import JSONable


# --------------------------------------------------------------------------------------------------------------------

class Command(JSONable):
    """
    An abstraction over Rocco Z21 DCC command datasets
    """


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def construct(cls, header: Header, *argv):
        try:
            meta = CommandMetadata.find(header)
        except TypeError:
            raise TypeError(f'unsupported header: {header}')

        if len(argv) != meta.argc:
            raise ValueError(f'{header} requires {meta.argc} got: {len(argv)}')

        argv = meta.argv_builder(*argv)

        return cls(header, *argv)


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
        argv = jdict.get('argv')

        return cls(header, *argv)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, header: Header, *argv: int):
        self._header = header
        self._argv = argv


    def __eq__(self, other: Any):
        try:
            return self.header == other.header and self.argv == other.argv
        except (AttributeError, TypeError):
            return False


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def dataset(self) -> Dataset:
        data = struct.pack(self.data_format, *self.argv)
        return Dataset(self.header, data)


    @property
    def data_format(self):
        return self.meta.data_format


    @property
    def report_type(self):
        return self.meta.report_type


    # ----------------------------------------------------------------------------------------------------------------

    def as_json(self, **kwargv):
        jdict = OrderedDict()

        jdict['type'] = self.type_name()

        jdict['header'] = self.header.name
        jdict['argv'] = self.argv

        return jdict


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def meta(self):
        return CommandMetadata.find(self.header)


    @property
    def header(self):
        return self._header


    @property
    def argv(self):
        return self._argv


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *argv, **kwargv):
        return f'Command:{{header:{self.header.name}, argv:{self.argv}}}'


# --------------------------------------------------------------------------------------------------------------------

class XCommand(Command):
    """
    An enumeration of all the supported commands
    """


    @classmethod
    def construct_x(cls, x_header: XHeader, *argv: int):
        try:
            meta = XCommandMetadata.find_x(x_header)
        except TypeError:
            raise TypeError(f'unsupported header: {x_header}')

        if len(argv) != meta.argc:
            raise ValueError(f'{x_header} requires {meta.argc} got: {len(argv)}')

        argv = meta.argv_builder(*argv)

        return cls(x_header, *argv)


    @classmethod
    def construct_from_jdict(cls, jdict):
        if not jdict:
            return None

        type_name = jdict.get('type')

        if type_name != cls.type_name():
            raise TypeError(f'required type:{cls.type_name()} got:{type_name}')

        # may raise KeyError
        x_header = XHeader[jdict['x_header']]
        argv = jdict.get('argv')

        return cls(x_header, *argv)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, x_header: XHeader, *argv):
        super().__init__(Header.LAN_X, *argv)
        self.__x_header = x_header


    def __eq__(self, other: Any):
        try:
            return self.header == other.header and self.x_header == other.x_header and self.argv == other.argv
        except (AttributeError, TypeError):
            return False


    # ----------------------------------------------------------------------------------------------------------------

    def as_json(self, **kwargv):
        jdict = OrderedDict()

        jdict['type'] = self.type_name()

        jdict['x_header'] = self.x_header.name
        jdict['argv'] = self.argv

        return jdict


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def dataset(self) -> XDataset:
        data = struct.pack(self.data_format, *self.argv)
        return XDataset.construct_from_command(self.header, self.x_header, data)


    @property
    def data_format(self):
        return self.meta.data_format


    @property
    def report_type(self):
        return self.meta.report_type


    # ----------------------------------------------------------------------------------------------------------------


    @property
    def meta(self):
        return XCommandMetadata.find_x(self.x_header)


    @property
    def x_header(self):
        return self.__x_header


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *argv, **kwargv):
        return f'XCommand:{{header:{self.header.name}, x_header:{self.x_header.name}, argv:{self.argv}}}'
