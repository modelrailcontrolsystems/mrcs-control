"""
Created on 20 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

A constructor to unmarshall equipment reports from Z21 datasets

Classes in support of the Rocco Z21 DCC command station:
https://www.z21.eu/en/products/z21

Based on code:
https://github.com/botmonster/z21aio/tree/main
https://gitlab.com/z21-fpm/z21_python
"""

from mrcs_control.dcc.z21.command.dataset import Dataset
from mrcs_control.dcc.z21.command.header import Header, XHeader
from mrcs_control.dcc.z21.equipment.block.z21_block_report import Z21BlockReport
from mrcs_control.dcc.z21.equipment.control_router.z21_control_router_report import Z21ControlRouterReport
from mrcs_control.dcc.z21.equipment.motive_power_unit.z21_mpu_configuration_report import Z21MPUConfigurationReport
from mrcs_control.dcc.z21.equipment.motive_power_unit.z21_mpu_decoder_report import Z21MPUDecoderReport
from mrcs_control.dcc.z21.equipment.track.z21_track_report import Z21TrackReport
from mrcs_control.dcc.z21.equipment.turnout.z21_turnout_report import Z21TurnoutReport
from mrcs_core.data.json import JSONable


# --------------------------------------------------------------------------------------------------------------------

class Z21EquipmentReport(object):
    """
    A constructor to unmarshall equipment reports from Z21 datasets
    """

    __HEADER_MAPPING = {
        Header.LAN_CAN_DETECTOR: Z21BlockReport,
        Header.LAN_SYSTEMSTATE_DATACHANGED: Z21ControlRouterReport,
        Header.LAN_RAILCOM_DATACHANGED: Z21MPUDecoderReport,
    }

    __X_HEADER_MAPPING = {
        XHeader.LAN_X_LOCO_INFO: Z21MPUConfigurationReport,
        XHeader.LAN_X_BC_TRACK_POWER: Z21TrackReport,
        XHeader.LAN_X_TURNOUT_INFO: Z21TurnoutReport
    }


    @classmethod
    def __class_find(cls, header: Header, x_header: XHeader):
        if header == Header.LAN_X:
            return cls.__X_HEADER_MAPPING[x_header]

        return cls.__HEADER_MAPPING[header]


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def construct_from_dataset(cls, dataset: Dataset) -> JSONable:
        try:
            equipment_cls = cls.__class_find(dataset.header, dataset.x_header)

        except KeyError:
            raise TypeError(f'unsupported header:{dataset.header}, x_header:{dataset.x_header}')

        return equipment_cls.construct_from_dataset(dataset)
