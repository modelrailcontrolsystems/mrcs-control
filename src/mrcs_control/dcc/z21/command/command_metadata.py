"""
Created on 25 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

The CommandMetadata and XCommandMetadata classes provide information that is common to each command with a given
header, including how to build the command object, and what responses are expected from the Z21.
The catalogues indicate which commands are supported.

Note that the argc field indicates the number of arguments that the Command or XCommand factory method should require.
Other arguments may be supplied by a custom argv builder method.

https://docs.python.org/3/library/struct.html#format-characters

Classes in support of the Rocco Z21 DCC control router station:
https://www.z21.eu/en/products/z21
"""

from typing import Dict, Protocol, Type

from mrcs_control.dcc.z21.command.header import Header, XHeader
from mrcs_core.equipment.control_router.control_router_report import ControlRouterReport
from mrcs_core.equipment.motive_power_unit.mpu_configuration_report import MPUConfigurationReport
from mrcs_core.equipment.motive_power_unit.mpu_enums import ThrottleSteps
from mrcs_core.equipment.track.track_report import TrackReport
from mrcs_core.equipment.turnout.turnout_enums import TurnoutPosition
from mrcs_core.equipment.turnout.turnout_report import TurnoutReport


# --------------------------------------------------------------------------------------------------------------------

class ArgvBuilder(Protocol):

    def __call__(self, *args: int) -> tuple[int, ...]: ...


# --------------------------------------------------------------------------------------------------------------------

class CommandMetadata(object):
    """
    Information that is common to each Command with a given header.
    """

    __CATALOG: Dict[Header, CommandMetadata]


    @classmethod
    def init(cls):
        cls.__CATALOG = {
            Header.LAN_LOGOFF: cls(Header.LAN_LOGOFF, 0, cls.argv_std, '', None),
            Header.LAN_SET_BROADCAST_FLAGS: cls(Header.LAN_SET_BROADCAST_FLAGS, 1, cls.argv_std, '<I', None),
            Header.LAN_SYSTEMSTATE_GETDATA:
                cls(Header.LAN_SYSTEMSTATE_GETDATA, 0, cls.argv_std, '', ControlRouterReport),
        }


    @classmethod
    def find(cls, header: Header):
        try:
            return cls.__CATALOG[header]
        except KeyError:
            raise TypeError(header.name)


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def argv_std(cls, *args: int) -> tuple[int, ...]:
        return args


    # ----------------------------------------------------------------------------------------------------------------


    def __init__(self, header: Header, argc: int, argv_builder: ArgvBuilder, data_format: str,
                 report_type: Type | None):
        self._header = header
        self._argc = argc
        self._argv_builder = argv_builder
        self._data_format = data_format
        self._report_type = report_type


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def header(self):
        return self._header


    @property
    def argc(self):
        return self._argc


    @property
    def argv_builder(self):
        return self._argv_builder


    @property
    def data_format(self):
        return self._data_format


    @property
    def report_type(self):
        return self._report_type


    # ----------------------------------------------------------------------------------------------------------------

    # noinspection PyUnresolvedReferences
    def __str__(self, *args, **kwargs):
        argv_builder = self.argv_builder.__name__
        report_type_name = None if self.report_type is None else self.report_type.__name__

        return (f'CommandMetadata:{{header:{self.header.name}, argc:{self.argc}, '
                f'argv_builder:{argv_builder}, data_format:{self.data_format}, report_type:{report_type_name}}}')


# --------------------------------------------------------------------------------------------------------------------

class XCommandMetadata(CommandMetadata):
    """
    Information that is common to each XCommand with a given x-header.
    """

    __CATALOG: Dict[XHeader, XCommandMetadata]


    @classmethod
    def init(cls):
        cls.__CATALOG = {
            XHeader.LAN_X_GET_LOCO: cls(XHeader.LAN_X_GET_LOCO, 1, cls.argv_get_loco, '>BH', MPUConfigurationReport),
            XHeader.LAN_X_SET_LOCO_FUNCTION: cls(XHeader.LAN_X_SET_LOCO_FUNCTION, 3, cls.argv_set_loco, '>BHB',
                                                 None),
            XHeader.LAN_X_SET_TRACK_POWER: cls(XHeader.LAN_X_SET_TRACK_POWER, 1, cls.argv_std, 'B', TrackReport),
            XHeader.LAN_X_SET_TURNOUT: cls(XHeader.LAN_X_SET_TURNOUT, 2, cls.argv_turnout, '>HB', TurnoutReport),
        }


    @classmethod
    def find_x(cls, x_header: XHeader):
        try:
            return cls.__CATALOG[x_header]
        except KeyError:
            raise TypeError(x_header.name)


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def argv_turnout(cls, *args: int) -> tuple[int, ...]:
        db2 = 0xa9 if args[1] == TurnoutPosition.P1 else 0xa8
        return args[0], db2


    @classmethod
    def argv_get_loco(cls, *args: int) -> tuple[int, ...]:
        db0 = 0xf0
        return db0, args[0]


    @classmethod
    def argv_set_loco(cls, *args: int) -> tuple[int, ...]:
        db0 = ThrottleSteps.STEPS_128.to_speed_byte()
        direction = 0x80 if args[1] == 1 else 0x00
        db3 = direction | args[2]
        return db0, args[0], db3


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, x_header: XHeader, argc: int, argv_builder: ArgvBuilder, data_format: str,
                 report_type: Type | None):
        super().__init__(Header.LAN_X, argc, argv_builder, data_format, report_type)
        self.__x_header = x_header


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def x_header(self):
        return self.__x_header


    # ----------------------------------------------------------------------------------------------------------------

    # noinspection PyUnresolvedReferences
    def __str__(self, *args, **kwargs):
        argv_builder = self.argv_builder.__name__
        report_type_name = None if self.report_type is None else self.report_type.__name__

        return (f'XCommandMetadata:{{header:{self.header.name}, x_header:{self.x_header.name}, argc:{self.argc}, '
                f'argv_builder:{argv_builder}, data_format:{self.data_format}, report_type:{report_type_name}}}')
