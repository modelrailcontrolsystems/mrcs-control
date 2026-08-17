"""
Created on 13 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

EquipmentReport: XHeader.LAN_X_TURNOUT_INFO

Reports a turnout state with a Dataset supplied by a Z21 DCC control router station.
Note that the turnout address is 1-based, not 0-based.

Classes in support of the Rocco Z21 DCC control router station:
https://www.z21.eu/en/products/z21

Based on code:
https://github.com/botmonster/z21aio/tree/main
https://gitlab.com/z21-fpm/z21_python
"""

import struct

from mrcs_control.dcc.z21.command.dataset import Dataset
from mrcs_core.equipment.turnout.turnout_enums import TurnoutPosition
from mrcs_core.equipment.turnout.turnout_report import TurnoutReport


# --------------------------------------------------------------------------------------------------------------------

class TurnoutReportBuilder(object):
    """
    Reports a turnout state with a Dataset supplied by a Z21 DCC control router station
    """


    @classmethod
    def construct_from_dataset(cls, dataset: Dataset) -> TurnoutReport:
        data = dataset.data

        if len(data) != 3:
            raise ValueError(f'Z21TurnoutReport data requires 3 bytes, got {data.hex(" ")}')

        turnout_address = struct.unpack('>H', data[:2])[0] + 1  # we use 1-based turnout addresses

        # may raise ValueError
        position = TurnoutPosition(data[2] & 0x03)

        return TurnoutReport(turnout_address, position)
