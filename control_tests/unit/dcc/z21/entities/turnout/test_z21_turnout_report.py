"""
Created on 13 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v unit/dcc/z21/entities/turnout/test_z21_turnout_state.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import unittest

from mrcs_control.dcc.z21.command.dataset import Dataset
from mrcs_control.dcc.z21.equipment.turnout.z21_turnout_report import Z21TurnoutReport


# --------------------------------------------------------------------------------------------------------------------

class TestZ21TurnoutReport(unittest.TestCase):

    def test_construct_turnout_p0(self):
        chars = bytes([0x09, 0x00, 0x40, 0x00, 0x43, 0x00, 0x00, 0x01, 0x42])
        obj1 = Dataset.construct_from_bytes(chars)
        obj2 = Z21TurnoutReport.construct_from_dataset(obj1)
        self.assertEqual('TurnoutReport:{address:0, position:P0}', str(obj2))


    def test_construct_turnout_p1(self):
        chars = bytes([0x09, 0x00, 0x40, 0x00, 0x43, 0x00, 0x00, 0x02, 0x41])
        obj1 = Dataset.construct_from_bytes(chars)
        obj2 = Z21TurnoutReport.construct_from_dataset(obj1)
        self.assertEqual('TurnoutReport:{address:0, position:P1}', str(obj2))


# --------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
