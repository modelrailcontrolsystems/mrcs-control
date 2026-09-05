"""
Created on 5 Sep 2026

@author: Bruno Beloff (bbeloff@me.com)

An enumeration of all the MPU node serial numbers
"""

from enum import IntEnum, unique

from mrcs_core.data.meta_enum import MetaEnum


# --------------------------------------------------------------------------------------------------------------------

@unique
class MPUNodeSerial(IntEnum, metaclass=MetaEnum):
    """
    An enumeration of all the MPU node serial numbers
    """

    NODE = 1
    MPU_STATUS = 2


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'{self.name}{{{self.value}}}'
