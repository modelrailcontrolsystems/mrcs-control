"""
Created on 6 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v unit/dcc/z21/command/test_dataset.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import unittest

from mrcs_control.dcc.z21.command.dataset import Dataset
from mrcs_control.dcc.z21.command.header import Header


# --------------------------------------------------------------------------------------------------------------------

class TestDataset(unittest.TestCase):

    def test_dataset(self):
        data = bytes([0x89, 0xd4, 0x05, 0x00, 0x04, 0x01, 0x00, 0x11, 0x00, 0x00])
        obj1 = Dataset(Header.LAN_CAN_DETECTOR, data=data)
        self.assertEqual('Dataset:{header:0x00c4 [LAN_CAN_DETECTOR], total_len:14, '
                         'data:89 d4 05 00 04 01 00 11 00 00}', str(obj1))


    def test_dataset_as_bytes(self):
        data = bytes([0x89, 0xd4, 0x05, 0x00, 0x04, 0x01, 0x00, 0x11, 0x00, 0x00])
        obj1 = Dataset(Header.LAN_CAN_DETECTOR, data=data)
        self.assertEqual('0e 00 c4 00 89 d4 05 00 04 01 00 11 00 00', obj1.as_bytes().hex(' '))


    def test_construct_dataset(self):
        chars = bytes([0x0e, 0x00, 0xc4, 0x00, 0x89, 0xd4, 0x05, 0x00, 0x04, 0x01, 0x00, 0x11, 0x00, 0x00])
        obj1 = Dataset.construct_from_bytes(chars)
        self.assertEqual('Dataset:{header:0x00c4 [LAN_CAN_DETECTOR], total_len:14, '
                         'data:89 d4 05 00 04 01 00 11 00 00}', str(obj1))


    def test_construct_x_dataset(self):
        chars = bytes([0x0f, 0x00, 0x40, 0x00, 0xef, 0x00, 0x04, 0x0c, 0xb5, 0x00, 0x00, 0x00, 0x00, 0x00, 0x52])
        obj1 = Dataset.construct_from_bytes(chars)
        self.assertEqual(
            'XDataset:{header:0x0040 [LAN_X], x_header:0x00ef [LAN_X_LOCO_INFO], total_len:15, '
            'data:00 04 0c b5 00 00 00 00 00, xor:0x52}',
            str(obj1))


# --------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
