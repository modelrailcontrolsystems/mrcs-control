"""
Created on 13 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

The track state, as reported by a Z21 DCC command station

Classes in support of the Rocco Z21 DCC command station:
https://www.z21.eu/en/products/z21

Based on code:
https://github.com/botmonster/z21aio/tree/main
https://gitlab.com/z21-fpm/z21_python
"""

from mrcs_control.dcc.z21.command.dataset import Dataset
from mrcs_core.equipment.track.track_mode import TrackMode
from mrcs_core.equipment.track.track_report import TrackReport


# --------------------------------------------------------------------------------------------------------------------

class Z21TrackReport(object):
    """
    The track state, as reported by a Z21 DCC command station
    """


    @classmethod
    def construct_from_dataset(cls, dataset: Dataset) -> TrackReport:
        data = dataset.data

        if len(data) != 1:
            raise ValueError(f'Z21TrackReport data requires 1 byte, got {data.hex(" ")}')

        # may raise ValueError
        mode = TrackMode(data[0])

        return TrackReport(mode)
