"""
Created on 25 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

A mapping between Rocco Z21 DCC commands and their report_types

Classes in support of the Rocco Z21 DCC command station:
https://www.z21.eu/en/products/z21
"""

from typing import Dict, Type

from mrcs_control.dcc.z21.command.header import Header, XHeader
from mrcs_core.equipment.control_router.control_router_state import ControlRouterState
from mrcs_core.equipment.track.track_state import TrackState


# --------------------------------------------------------------------------------------------------------------------

class CommandMetadata(object):
    """
    An enumeration of all the supported commands
    """

    __MAPPING: Dict[Header, CommandMetadata]


    @classmethod
    def init(cls):
        cls.__MAPPING = {
            Header.LAN_LOGOFF: cls(Header.LAN_LOGOFF, '', None),
            Header.LAN_SET_BROADCAST_FLAGS: cls(Header.LAN_SET_BROADCAST_FLAGS, '', None),
            Header.LAN_SYSTEMSTATE_GETDATA: cls(Header.LAN_SYSTEMSTATE_GETDATA, '', ControlRouterState),
        }


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def is_supported(cls, header: Header) -> bool:
        return header in cls.__MAPPING


    @classmethod
    def find(cls, header: Header):
        try:
            return cls.__MAPPING[header]
        except KeyError:
            raise TypeError(header.name)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, header: Header, data_format: str, report_type: Type | None):
        self._header = header
        self._data_format = data_format
        self._report_type = report_type


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def header(self):
        return self._header


    @property
    def data_format(self):
        return self._data_format


    @property
    def report_type(self):
        return self._report_type


    # ----------------------------------------------------------------------------------------------------------------

    # noinspection PyUnresolvedReferences
    def __str__(self, *args, **kwargs):
        report_type_name = None if self.report_type is None else self.report_type.__name__

        return (f'CommandMetadata:{{header:{self.header.name}, data_format:{self.data_format}, '
                f'report_type:{report_type_name}}}')


# --------------------------------------------------------------------------------------------------------------------

class XCommandMetadata(CommandMetadata):
    """
    An enumeration of all the supported commands
    """

    __MAPPING: Dict[XHeader, XCommandMetadata]


    @classmethod
    def init(cls):
        cls.__MAPPING = {
            XHeader.LAN_X_SET_TRACK_POWER: cls(XHeader.LAN_X_SET_TRACK_POWER, 'B', TrackState),
        }


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def is_supported(cls, x_header: XHeader) -> bool:
        return x_header in cls.__MAPPING


    @classmethod
    def find(cls, x_header: XHeader):
        try:
            return cls.__MAPPING[x_header]
        except KeyError:
            raise TypeError(x_header.name)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, x_header: XHeader, data_format: str, report_type: Type | None):
        super().__init__(Header.LAN_X, data_format, report_type)
        self.__x_header = x_header


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def x_header(self):
        return self.__x_header


    # ----------------------------------------------------------------------------------------------------------------

    # noinspection PyUnresolvedReferences
    def __str__(self, *args, **kwargs):
        report_type_name = None if self.report_type is None else self.report_type.__name__

        return (f'XCommandMetadata:{{header:{self.header.name}, x_header:{self.x_header.name}, '
                f'data_format:{self.data_format}, report_type:{report_type_name}}}')
