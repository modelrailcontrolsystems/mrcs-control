"""
Created on 4 Jul 2026

@author: Bruno Beloff (bbeloff@me.com)

A structured representation of an MPUStatus

{
    "type": "MPUStatus",
    "label": "EMR Class 08",
    "addr": 3,
    "functions": "+-+",
    "speed_setting": 12,
    "speed": 7,
    "reverse": true
"""

from mrcs_control.data.persistence import PersistentObject
from mrcs_control.equipment.motive_power_unit.mpu_status_persistence import MPUStatusPersistence
from mrcs_core.equipment.motive_power_unit.mpu_functions import MPUFunctions

from mrcs_core.equipment.motive_power_unit.mpu_status import MPUStatus


# --------------------------------------------------------------------------------------------------------------------

class PersistentMPUStatus(MPUStatus, MPUStatusPersistence, PersistentObject):
    """
    a structured representation of an MPUStatus
    """


    @classmethod
    def construct_from_db(cls, row):
        label, address, functions, speed_setting, speed, reverse = row
        return cls(label, address, MPUFunctions.construct_from_jdict(functions), speed_setting, speed, bool(reverse))


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, label: str, address: int, functions: MPUFunctions, speed_setting: int, speed: int,
                 reverse: bool):
        super().__init__(label, address, functions, speed_setting, speed, reverse)


    # ----------------------------------------------------------------------------------------------------------------

    def save(self):
        return super().insert(self)


    # ----------------------------------------------------------------------------------------------------------------

    def as_db_insert(self):
        return self.label, self.address, self.functions.as_json(), self.speed_setting, self.speed, self.reverse


    def as_db_update(self):
        return self.address, self.functions.as_json(), self.speed_setting, self.speed, self.reverse, self.label
