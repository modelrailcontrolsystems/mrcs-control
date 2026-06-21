"""
Created on 5 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

An enumeration of all the LAN and XLAN header values

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
class Header(IntEnum, metaclass=MetaEnum):
    """
    An enumeration of all the LAN header values
    """

    LAN_UNKNOWN = 0x00

    LAN_GET_SERIAL_NUMBER = 0x10
    LAN_GET_CODE = 0x18
    LAN_GET_HWINFO = 0x1A
    LAN_LOGOFF = 0x30
    LAN_DISCOVER_DEVICES = 0x35
    LAN_X = 0x40
    LAN_SET_BROADCAST_FLAGS = 0x50
    LAN_GET_BROADCAST_FLAGS = 0x51
    LAN_GET_LOCOMODE = 0x60
    LAN_SET_LOCOMODE = 0x61
    LAN_GET_TURNOUTMODE = 0x70
    LAN_SET_TURNOUTMODE = 0x71
    LAN_RMBUS_DATACHANGED = 0x80
    LAN_RMBUS_GETDATA = 0x81
    LAN_RMBUS_PROGRAMMODULE = 0x82
    LAN_SYSTEMSTATE_DATACHANGED = 0x84
    LAN_SYSTEMSTATE_GETDATA = 0x85
    LAN_RAILCOM_DATACHANGED = 0x88
    LAN_RAILCOM_GETDATA = 0x89
    LAN_LOCONET_Z21_RX = 0xA0
    LAN_LOCONET_Z21_TX = 0xA1
    LAN_LOCONET_FROM_LAN = 0xA2
    LAN_LOCONET_DISPATCH_ADDR = 0xA3
    LAN_LOCONET_DETECTOR = 0xA4
    LAN_BOOSTER_SET_POWER = 0xB2
    LAN_BOOSTER_GET_DESCRIPTION = 0xB8
    LAN_BOOSTER_SET_DESCRIPTION = 0xB9
    LAN_BOOSTER_SYSTEMSTATE_DATACHANGED = 0xBA
    LAN_BOOSTER_SYSTEMSTATE_GETDATA = 0xBB
    LAN_CAN_DETECTOR = 0xC4
    LAN_CAN_DEVICE_GET_DESCRIPTION = 0xC8
    LAN_CAN_DEVICE_SET_DESCRIPTION = 0xC9
    LAN_CAN_BOOSTER_SYSTEMSTATE_CHGD = 0xCA
    LAN_CAN_BOOSTER_SET_TRACKPOWER = 0xCB
    LAN_FAST_CLOCK_CONTROL = 0xCC
    LAN_FAST_CLOCK_DATA = 0xCD
    LAN_FAST_CLOCK_SETTINGS_GET = 0xCE
    LAN_FAST_CLOCK_SETTINGS_SET = 0xCF
    LAN_DECODER_GET_DESCRIPTION = 0xD8
    LAN_DECODER_SET_DESCRIPTION = 0xD9
    LAN_DECODER_SYSTEMSTATE_DATACHANGED = 0xDA
    LAN_DECODER_SYSTEMSTATE_GETDATA = 0xDB
    LAN_ZLINK_GET_HWINFO = 0xE8


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def construct(cls, int_value: int):
        try:
            return cls(int_value)
        except ValueError:
            return cls.LAN_UNKNOWN


# --------------------------------------------------------------------------------------------------------------------

@unique
class XHeader(IntEnum, metaclass=MetaEnum):
    """
    An enumeration of all the XLAN header values
    """

    LAN_X_UNKNOWN = 0x00

    LAN_X_GET_VERSION__GET_STATUS__SET_TRACK_POWER = 0x21
    LAN_X_DCC_READ_REGISTER = 0x22
    LAN_X_CV_REGISTER = 0x23
    LAN_X_CV_BYTE = 0x24
    LAN_X_TURNOUT_INFO = 0x43
    LAN_X_ACCESSORY_INFO = 0x44
    LAN_X_SET_TURNOUT = 0x53
    LAN_X_SET_EXT_ACCESSORY = 0x54
    LAN_X_BC_TRACK_POWER = 0x61
    LAN_X_STATUS_CHANGED = 0x62
    LAN_X_GET_VERSION_REPLY = 0x63
    LAN_X_CV_RESULT = 0x64
    LAN_X_SET_STOP = 0x80
    LAN_X_BC_STOPPED = 0x81
    LAN_X_SET_LOCO_E_STOP = 0x92
    LAN_X_PURGE_LOCO = 0xE3
    LAN_X_SET_LOCO_FUNCTION = 0xE4
    LAN_X_SET_LOCO_BINARY_STATE = 0xE5
    LAN_X_CV_POM = 0xE6
    LAN_X_LOCO_INFO = 0xEF
    LAN_X_GET_FIRMWARE_VERSION = 0xF1
    LAN_X_GET_FIRMWARE_VERSION_REPLY = 0xF3


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def construct(cls, int_value: int):
        try:
            return cls(int_value)
        except ValueError:
            return cls.LAN_X_UNKNOWN
