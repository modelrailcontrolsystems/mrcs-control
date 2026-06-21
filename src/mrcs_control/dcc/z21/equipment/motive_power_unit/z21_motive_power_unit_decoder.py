"""
Created on 18 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

A DCC motive power unit (MPU) decoder state, as reported by a Z21 DCC command station

Classes in support of the Rocco Z21 DCC command station:
https://www.z21.eu/en/products/z21

Based on code:
https://github.com/botmonster/z21aio/tree/main
https://gitlab.com/z21-fpm/z21_python
"""

import struct

from mrcs_control.dcc.z21.command.dataset import Dataset
from mrcs_core.equipment.motive_power_unit.motive_power_unit_decoder import MotivePowerUnitDecoder


# --------------------------------------------------------------------------------------------------------------------

class Z21MotivePowerUnitDecoder(object):
    """
    A DCC motive power unit (MPU) decoder state, as reported by a Z21 DCC command station
    """


    @classmethod
    def construct_from_dataset(cls, dataset: Dataset) -> MotivePowerUnitDecoder:
        data = dataset.data

        if len(data) != 13:
            raise ValueError(f'Z21MotivePowerUnitDecoder data requires 13 bytes, got {data.hex(" ")}')

        address, receive_count, error_count, _, opts, speed, qos, _ = struct.unpack('<HLHBBBBB', data)

        return MotivePowerUnitDecoder(address, receive_count, error_count, opts, speed, qos)
