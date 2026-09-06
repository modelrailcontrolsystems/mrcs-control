"""
Created on 6 Sep 2026

@author: Bruno Beloff (bbeloff@me.com)

An enumeration of all the telemetry node serial numbers
"""

from enum import IntEnum, unique

from mrcs_core.data.meta_enum import MetaEnum


# --------------------------------------------------------------------------------------------------------------------

@unique
class TelemetryNodeSerial(IntEnum, metaclass=MetaEnum):
    """
    An enumeration of all the telemetry node serial numbers
    """

    NODE = 1
    MPU_ASPECT = 2


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'{self.name}{{{self.value}}}'
