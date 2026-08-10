"""
Created on 20 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

A constructor to unmarshall equipment reports from Z21 datasets
The mappings should be kept in sync with the source code in ControlRouterIdentity.

Classes in support of the Rocco Z21 DCC control router station:
https://www.z21.eu/en/products/z21

Based on code:
https://github.com/botmonster/z21aio/tree/main
https://gitlab.com/z21-fpm/z21_python
"""

from mrcs_control.dcc.z21.command.dataset import Dataset
from mrcs_control.dcc.z21.command.header import Header, XHeader
from mrcs_control.dcc.z21.equipment.block.block_report import BlockReportBuilder
from mrcs_control.dcc.z21.equipment.control_router.control_router_report import ControlRouterReportBuilder
from mrcs_control.dcc.z21.equipment.motive_power_unit.mpu_configuration_report import \
    MPUConfigurationReportBuilder
from mrcs_control.dcc.z21.equipment.motive_power_unit.mpu_decoder_report import MPUDecoderReportBuilder
from mrcs_control.dcc.z21.equipment.track.track_report import TrackReportBuilder
from mrcs_control.dcc.z21.equipment.turnout.turnout_report import TurnoutReportBuilder
from mrcs_core.data.json import JSONable


# --------------------------------------------------------------------------------------------------------------------

class EquipmentReport(object):
    """
    A constructor to unmarshall equipment reports from Z21 datasets
    """

    __HEADER_MAPPING = {
        Header.LAN_CAN_DETECTOR: BlockReportBuilder,
        Header.LAN_SYSTEMSTATE_DATACHANGED: ControlRouterReportBuilder,
        Header.LAN_RAILCOM_DATACHANGED: MPUDecoderReportBuilder,
    }

    __X_HEADER_MAPPING = {
        XHeader.LAN_X_LOCO_INFO: MPUConfigurationReportBuilder,
        XHeader.LAN_X_BC_TRACK_POWER: TrackReportBuilder,
        XHeader.LAN_X_TURNOUT_INFO: TurnoutReportBuilder
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
            builder = cls.__class_find(dataset.header, dataset.x_header)

        except KeyError:
            raise TypeError(f'unsupported header:{dataset.header}, x_header:{dataset.x_header}')

        return builder.construct_from_dataset(dataset)
