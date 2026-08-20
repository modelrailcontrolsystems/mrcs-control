"""
Created on 13 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

EquipmentReport: Header.LAN_CAN_DETECTOR

Reports block occupany with a Dataset supplied by a Z21 DCC control router station

Based on the Roco 10808 detector:
https://www.roco.cc/ren/products/control/accessories/10808-z21-detector.html

Classes in support of the Rocco Z21 DCC control router station:
https://www.z21.eu/en/products/z21
"""

import struct

from mrcs_control.dcc.z21.command.dataset import Dataset
from mrcs_control.dcc.z21.equipment.block.z21_block_occupant import Z21BlockOccupant
from mrcs_core.equipment.block.block_enums import BlockVoltage
from mrcs_core.equipment.block.block_id import BlockID
from mrcs_core.equipment.block.block_report import BlockOccupancyReport, BlockVoltageReport


# --------------------------------------------------------------------------------------------------------------------

class BlockReportBuilder(object):
    """
    Reports block occupany with a Dataset supplied by a Z21 DCC control router station
    """


    @classmethod
    def construct_from_dataset(cls, dataset: Dataset) -> BlockVoltageReport | BlockOccupancyReport:
        data = dataset.data

        if len(data) != 10:
            raise ValueError(f'Z21BlockReport data requires 10 bytes, got {data.hex(" ")}')

        network_id, address, port, msg_type, value_1, value_2 = struct.unpack('<HHBBHH', data)

        detector_address = address + 1
        detector_channel = port + 1

        id = BlockID(detector_address, detector_channel, network_id)

        if msg_type == 0x01:
            voltage = BlockVoltage(value_1)
            return BlockVoltageReport(id, voltage)

        occupant_group = msg_type & 0x0f
        occupant1 = Z21BlockOccupant.construct_from_data(value_1)
        occupant2 = Z21BlockOccupant.construct_from_data(value_2)
        occupants = sorted([occupant for occupant in (occupant1, occupant2) if occupant.has_mpu_address()])
        # TODO: check what happens if this is a subsequent Z21BlockOccupant

        return BlockOccupancyReport(id, occupant_group, occupants)
