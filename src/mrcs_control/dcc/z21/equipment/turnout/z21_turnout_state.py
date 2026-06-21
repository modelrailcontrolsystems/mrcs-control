"""
Created on 13 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

A turnout state, as reported by a Z21 DCC command station

Classes in support of the Rocco Z21 DCC command station:
https://www.z21.eu/en/products/z21

Based on code:
https://github.com/botmonster/z21aio/tree/main
https://gitlab.com/z21-fpm/z21_python
"""
import struct

from mrcs_control.dcc.z21.command.dataset import Dataset
from mrcs_core.equipment.turnout.turnout_position import TurnoutPosition
from mrcs_core.equipment.turnout.turnout_state import TurnoutState


# --------------------------------------------------------------------------------------------------------------------

class Z21TurnoutState(object):
    """
    A turnout state, as reported by a Z21 DCC command station
    """


    @classmethod
    def construct_from_dataset(cls, dataset: Dataset) -> TurnoutState:
        data = dataset.data

        if len(data) != 3:
            raise ValueError(f'Z21TurnoutState data requires 3 bytes, got {data.hex(" ")}')

        address = struct.unpack('<H', data[:2])[0]

        # may raise ValueError
        position = TurnoutPosition(data[2] & 0x03)

        return TurnoutState(address, position)
