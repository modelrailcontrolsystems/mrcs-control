"""
Created on 4 Jul 2026

@author: Bruno Beloff (bbeloff@me.com)

A structured representation of an MPUStatus

{
    "type": "MPUStatus",
    "label": "GW158",
    "addr": 8,
    "functions": "+-+",
    "speed_setting": 31,
    "reported_speed": 7,
    "actual_speed": 3.6,
    "direction": FORWARD
}
"""

from typing import Self

from mrcs_control.data.persistence import PersistentObject
from mrcs_control.equipment.motive_power_unit.mpu_status_persistence import MPUStatusPersistence
from mrcs_core.equipment.motive_power_unit.mpu_enums import MPUDirection
from mrcs_core.equipment.motive_power_unit.mpu_functions import MPUFunctions
from mrcs_core.equipment.motive_power_unit.mpu_status import MPUStatus


# --------------------------------------------------------------------------------------------------------------------

class PersistentMPUStatus(MPUStatus, MPUStatusPersistence, PersistentObject):
    """
    a structured representation of an MPUStatus
    """


    @classmethod
    def type_name(cls) -> str:
        return MPUStatus.type_name()  # Persistent classes are for internal use only - advertise the base class


    @classmethod
    def narrow(cls, mpu: MPUStatus) -> Self:
        return cls(mpu.label, mpu.mpu_address, mpu.functions, mpu.speed_setting, mpu.reported_speed, mpu.actual_speed,
                   mpu.direction)


    @classmethod
    def construct_from_db(cls, row, *child_rows) -> Self:
        label, mpu_address, functions, speed_setting, reported_speed, actual_speed, direction = row

        return cls(label, mpu_address, MPUFunctions.construct_from_jdict(functions), speed_setting, reported_speed,
                   actual_speed, MPUDirection[direction])


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, label: str, mpu_address: int, functions: MPUFunctions, speed_setting: int | None,
                 reported_speed: int | None, actual_speed: float | None, direction: MPUDirection):
        super().__init__(label, mpu_address, functions, speed_setting, reported_speed, actual_speed, direction)


    # ----------------------------------------------------------------------------------------------------------------

    def save(self) -> None:
        type(self).insert(self)


    # ----------------------------------------------------------------------------------------------------------------

    def as_db_insert(self):
        return (self.label, self.mpu_address, self.functions.as_json(), self.speed_setting, self.reported_speed,
                self.actual_speed, self.direction.name)


    def as_db_update(self):
        raise NotImplementedError('update is provided by MPUConfigurationReport, MPUDecoderReport')
