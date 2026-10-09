"""
Created on 7 Oct 2026

@author: Bruno Beloff (bbeloff@me.com)

EquipmentReport: XHeader.LAN_X_CV_RESULT

Reports a configuration variable with a Dataset supplied by a Z21 DCC control router station.

Classes in support of the Rocco Z21 DCC control router station:
https://www.z21.eu/en/products/z21
"""

import struct

from mrcs_control.dcc.z21.command.dataset import Dataset
from mrcs_core.equipment.conviguration_variable.cv_report import CVReport


# --------------------------------------------------------------------------------------------------------------------

class CVReportBuilder(object):
    """
    Reports a configuration variable with a Dataset supplied by a Z21 DCC control router station
    """


    @classmethod
    def construct_from_dataset(cls, dataset: Dataset) -> CVReport:
        data = dataset.data

        if len(data) != 4:
            raise ValueError(f'data requires 4 bytes, got {data.hex(" ")}')

        cv_address = struct.unpack('>H', data[1:3])[0] + 1  # 1-based turnout addresses
        value = int(data[3])

        return CVReport(cv_address, value)
