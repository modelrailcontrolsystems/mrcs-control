"""
Created on 13 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

EquipmentReport: XHeader.LAN_X_BC_TRACK_POWER

Reports the track state with a Dataset supplied by a Z21 DCC control router station. Or does it?

The LAN_X headers LAN_X_BC_TRACK_POWER and LAN_X_UNKNOWN_COMMAND share the same value (0x61). Duh. So we attempt to
build a TrackReport, if we can't, we build an InvalidRequestReport instead.

Classes in support of the Rocco Z21 DCC control router station:
https://www.z21.eu/en/products/z21

Based on code:
https://github.com/botmonster/z21aio/tree/main
https://gitlab.com/z21-fpm/z21_python
"""

from mrcs_control.dcc.z21.command.dataset import Dataset
from mrcs_core.equipment.error.invalid_request_report import InvalidRequestReport
from mrcs_core.equipment.track.track_enums import TrackMode
from mrcs_core.equipment.track.track_report import TrackReport


# --------------------------------------------------------------------------------------------------------------------

class TrackReportBuilder(object):
    """
    Reports the track state with a Dataset supplied by a Z21 DCC control router station
    ... or an InvalidRequestReport
    """


    @classmethod
    def construct_from_dataset(cls, dataset: Dataset) -> TrackReport | InvalidRequestReport:
        data = dataset.data

        if len(data) != 1:
            raise ValueError(f'data requires 1 byte, got {data.hex(" ")}')

        try:
            mode = TrackMode(data[0])
        except ValueError:
            report = InvalidRequestReport(data[0])
            return report

        return TrackReport(mode)
