"""
Created on 13 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

EquipmentReport: XHeader.LAN_X_BC_TRACK_POWER

Reports the track state with a Dataset supplied by a Z21 DCC control router station

Classes in support of the Rocco Z21 DCC control router station:
https://www.z21.eu/en/products/z21

Based on code:
https://github.com/botmonster/z21aio/tree/main
https://gitlab.com/z21-fpm/z21_python
"""

from mrcs_control.dcc.z21.command.dataset import Dataset
from mrcs_core.equipment.track.track_enums import TrackMode
from mrcs_core.equipment.track.track_report import TrackReport


# --------------------------------------------------------------------------------------------------------------------

class TrackReportBuilder(object):
    """
    Reports the track state with a Dataset supplied by a Z21 DCC control router station
    """


    @classmethod
    def construct_from_dataset(cls, dataset: Dataset) -> TrackReport:
        data = dataset.data

        if len(data) != 1:
            raise ValueError(f'Z21TrackReport data requires 1 byte, got {data.hex(" ")}')

        # may raise ValueError
        mode = TrackMode(data[0])

        return TrackReport(mode)
