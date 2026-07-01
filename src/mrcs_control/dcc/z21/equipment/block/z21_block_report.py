"""
Created on 13 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

Block occupany detector reports, as reported by a Z21 DCC command station

Based on the Roco 10808 detector:
https://www.roco.cc/ren/products/control/accessories/10808-z21-detector.html

Classes in support of the Rocco Z21 DCC command station:
https://www.z21.eu/en/products/z21
"""

import struct

from mrcs_control.dcc.z21.command.dataset import Dataset
from mrcs_control.dcc.z21.equipment.block.z21_block_occupant_report import Z21BlockOccupantReport
from mrcs_core.equipment.block.block_report import BlockOccupancyReport, BlockStatusReport
from mrcs_core.equipment.block.block_status import BlockStatus


# --------------------------------------------------------------------------------------------------------------------

class Z21BlockReport(object):
    """
    Block occupany detector reports, as reported by a Z21 DCC command station
    """


    @classmethod
    def construct_from_dataset(cls, dataset: Dataset) -> BlockStatusReport | BlockOccupancyReport:
        data = dataset.data

        if len(data) != 10:
            raise ValueError(f'Z21BlockReport data requires 10 bytes, got {data.hex(" ")}')

        network_id, address, port, msg_type, value_1, value_2 = struct.unpack('<HHBBHH', data)

        reporter_address = address + 1
        reporter_input = port + 1

        if msg_type == 0x01:
            status = BlockStatus(value_1)
            return BlockStatusReport(network_id, reporter_address, reporter_input, status)

        occupant_group = msg_type & 0x0f
        occupant1 = Z21BlockOccupantReport.construct_from_data(value_1)
        occupant2 = Z21BlockOccupantReport.construct_from_data(value_2)
        occupants = sorted([occupant for occupant in (occupant1, occupant2) if occupant.has_address()])

        return BlockOccupancyReport(network_id, reporter_address, reporter_input, occupant_group, occupants)
