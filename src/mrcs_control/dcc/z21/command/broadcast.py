"""
Created on 6 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

An enumeration of all the broadcast flags

Classes in support of the Rocco Z21 DCC command station:
https://www.z21.eu/en/products/z21

Based on code:
https://github.com/botmonster/z21aio/tree/main
https://gitlab.com/z21-fpm/z21_python
"""

from enum import IntEnum, unique

from mrcs_core.data.meta_enum import MetaEnum


# --------------------------------------------------------------------------------------------------------------------

@unique
class Broadcast(IntEnum, metaclass=MetaEnum):
    """
    An enumeration of all the broadcast flags
    """

    NONE = 0x00000000

    TRACK = 0x00000001
    RMBUS_DATA = 0x00000002
    RAILCOM_DATA = 0x00000004
    SYSTEM_STATE = 0x00000100
    X_LOCO_INFO_ALL = 0x00010000
    LOCONET_BASIC = 0x01000000
    LOCONET_LOCO = 0x02000000
    LOCONET_SWITCH = 0x04000000
    LOCONET_OCCUPANCY = 0x08000000
    RAILCOM_DATA_ALL = 0x00040000
    CAN_DETECTOR = 0x00080000
    CAN_BOOSTER_SYSTEM_STATE = 0x00020000
    FAST_CLOCK_DATA = 0x00000010
