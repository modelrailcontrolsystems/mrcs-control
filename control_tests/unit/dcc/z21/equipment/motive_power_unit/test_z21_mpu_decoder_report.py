"""
Created on 31 Aug 2026

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v unit/dcc/z21/entities/motive_power_unit/test_z21_mpu_decoder_report.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import unittest

from mrcs_control.dcc.z21.command.dataset import Dataset
from mrcs_control.dcc.z21.equipment.motive_power_unit.mpu_decoder_report import MPUDecoderReportBuilder


# --------------------------------------------------------------------------------------------------------------------

class TestZ21MPUDecoderReport(unittest.TestCase):

    def test_construct(self):
        chars = bytes([0x11, 0x00, 0x88, 0x00, 0x34, 0x12, 0xc8, 0x01, 0x00, 0x00, 0x15, 0x03, 0x00, 0xab, 0x5a,
                       0x05, 0x00])
        obj1 = Dataset.construct_from_bytes(chars)
        obj2 = MPUDecoderReportBuilder.construct_from_dataset(obj1)
        self.assertEqual('MPUDecoderReport:{mpu_address:4660, receive_count:456, error_count:789, opts:0xab, '
                         'speed:90, qos:5}', str(obj2))


# --------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
