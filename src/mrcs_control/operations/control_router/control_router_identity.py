"""
Created on 9 Aug 2026

@author: Bruno Beloff (bbeloff@me.com)

A mapping of Z21 reports to control router messaging source serial numbers.
The mapping should be kept in sync with the source code in Z21EquipmentReport.
"""

from enum import IntEnum, unique

from mrcs_core.data.equipment_identity import EquipmentIdentifier, EquipmentType
from mrcs_core.data.json import JSONable
from mrcs_core.data.meta_enum import MetaEnum
from mrcs_core.equipment.block.block_report import BlockOccupancyReport, BlockVoltageReport
from mrcs_core.equipment.control_router.control_router_report import ControlRouterReport
from mrcs_core.equipment.motive_power_unit.mpu_configuration_report import MPUConfigurationReport
from mrcs_core.equipment.motive_power_unit.mpu_decoder_report import MPUDecoderReport
from mrcs_core.equipment.track.track_report import TrackReport
from mrcs_core.equipment.turnout.turnout_report import TurnoutReport


# --------------------------------------------------------------------------------------------------------------------

@unique
class ControlRouterSerial(IntEnum, metaclass=MetaEnum):
    """
    An enumeration of all the control router serial numbers
    """

    Router = 1

    Unclassified = 2
    Common = 3

    System = 4
    Track = 5  # TODO: separate into Block and Turnout
    Signal = 6
    MPU = 7


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'{self.name}{{{self.value}}}'


# --------------------------------------------------------------------------------------------------------------------

@unique
class ControlRouterIdentity(IntEnum, metaclass=MetaEnum):
    """
    a mapping of Z21 reports to control router messaging source serial numbers
    """

    __MAPPING: dict[type[JSONable], EquipmentIdentifier] = {
        ControlRouterReport: EquipmentIdentifier(EquipmentType.CRT, None, ControlRouterSerial.System),
        BlockOccupancyReport: EquipmentIdentifier(EquipmentType.CRT, None, ControlRouterSerial.Track),
        BlockVoltageReport: EquipmentIdentifier(EquipmentType.CRT, None, ControlRouterSerial.Track),
        MPUDecoderReport: EquipmentIdentifier(EquipmentType.CRT, None, ControlRouterSerial.MPU),
        MPUConfigurationReport: EquipmentIdentifier(EquipmentType.CRT, None, ControlRouterSerial.MPU),
        TrackReport: EquipmentIdentifier(EquipmentType.CRT, None, ControlRouterSerial.Track),
        TurnoutReport: EquipmentIdentifier(EquipmentType.CRT, None, ControlRouterSerial.Track)
    }


    @classmethod
    def get(cls, report: JSONable) -> EquipmentIdentifier:
        try:
            return cls.__MAPPING[type(report)]
        except KeyError:
            return EquipmentIdentifier(EquipmentType.CRT, None, ControlRouterSerial.Unclassified)
