"""
Created on 18 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

Reports a motive power unit (MPU) decoder state from a Z21 DCC control router station

Classes in support of the Rocco Z21 DCC control router station:
https://www.z21.eu/en/products/z21

Based on code:
https://github.com/botmonster/z21aio/tree/main
https://gitlab.com/z21-fpm/z21_python
"""

import struct

from mrcs_control.dcc.z21.command.dataset import Dataset
from mrcs_core.equipment.motive_power_unit.mpu_decoder_report import MPUDecoderReport


# TODO: needs test coverage
# --------------------------------------------------------------------------------------------------------------------

class MPUDecoderReportBuilder(object):
    """
    Reports a motive power unit (MPU) decoder state with a Dataset supplied by a Z21 DCC control router station
    """


    @classmethod
    def construct_from_dataset(cls, dataset: Dataset) -> MPUDecoderReport:
        data = dataset.data

        if len(data) != 13:
            raise ValueError(f'Z21MPUDecoderReport data requires 13 bytes, got {data.hex(" ")}')

        address, receive_count, error_count, _, opts, speed, qos, _ = struct.unpack('<HLHBBBBB', data)
        mpu_address = address & 0x3fff

        return MPUDecoderReport(mpu_address, receive_count, error_count, opts, speed, qos)
