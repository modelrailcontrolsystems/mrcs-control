"""
Created on 13 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v unit/dcc/z21/entities/block_occupancy/test_z21_block_report.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import unittest

from mrcs_control.dcc.z21.command.dataset import Dataset
from mrcs_control.dcc.z21.equipment.block.z21_block_report import Z21BlockReport


# --------------------------------------------------------------------------------------------------------------------

class TestZ21BlockReport(unittest.TestCase):

    def test_construct_block_status_report_4_0(self):
        chars = bytes([0x0e, 0x00, 0xc4, 0x00, 0x78, 0xdb, 0x04, 0x00, 0x00, 0x01, 0x00, 0x11, 0x00, 0x00])
        obj1 = Dataset.construct_from_bytes(chars)
        obj2 = Z21BlockReport.construct_from_dataset(obj1)
        self.assertEqual('BlockStatusReport:{network_id:0xdb78, reporter_address:5, reporter_input:1, '
                         'status:OCCUPIED_WITH_VOLTAGE}', str(obj2))


    def test_construct_block_status_report_5_5(self):
        chars = bytes([0x0e, 0x00, 0xc4, 0x00, 0x89, 0xd4, 0x05, 0x00, 0x05, 0x01, 0x00, 0x11, 0x00, 0x00])
        obj1 = Dataset.construct_from_bytes(chars)
        obj2 = Z21BlockReport.construct_from_dataset(obj1)
        self.assertEqual('BlockStatusReport:{network_id:0xd489, reporter_address:6, reporter_input:6, '
                         'status:OCCUPIED_WITH_VOLTAGE}', str(obj2))


    def test_construct_block_occupancy_report_03_04(self):
        chars = bytes([0x0e, 0x00, 0xc4, 0x00, 0x89, 0xd4, 0x05, 0x00, 0x06, 0x11, 0x04, 0x80, 0x03, 0x80])
        obj1 = Dataset.construct_from_bytes(chars)
        obj2 = Z21BlockReport.construct_from_dataset(obj1)
        self.assertEqual('BlockOccupancyReport:{network_id:0xd489, reporter_address:6, reporter_input:7, '
                         'occupant_group:1, occupants:[BlockOccupant:{address:3, face:FWD}, '
                         'BlockOccupant:{address:4, face:FWD}]}', str(obj2))


# --------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
