"""
Created on 5 Sep 2026

@author: Bruno Beloff (bbeloff@me.com)

An enumeration of all the track node serial numbers
"""

from enum import IntEnum, StrEnum, unique

from mrcs_core.data.meta_enum import MetaEnum


# --------------------------------------------------------------------------------------------------------------------

@unique
class TrackNodeSerial(IntEnum, metaclass=MetaEnum):
    """
    An enumeration of all the track node serial numbers
    """

    NODE = 1
    BLOCK_STATUS = 2
    TURNOUT_STATUS = 3


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'{self.name}{{{self.value}}}'


# --------------------------------------------------------------------------------------------------------------------

@unique
class TrackNodeCommand(StrEnum, metaclass=MetaEnum):
    """
    An enumeration of all the track node serial numbers
    """

    FIND_ALL_TURNOUTS = 'FIND_ALL_TURNOUTS'
    FIND_ALL_BLOCKS = 'FIND_ALL_BLOCKS'
