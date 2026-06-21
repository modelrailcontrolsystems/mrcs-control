"""
Created on 6 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v dcc/z21/entities/motive_power_unit/test_z21_motive_power_unit_state.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import unittest

from mrcs_control.dcc.z21.command.dataset import Dataset
from mrcs_control.dcc.z21.equipment.motive_power_unit.z21_motive_power_unit_state import Z21MotivePowerUnitState


# --------------------------------------------------------------------------------------------------------------------

class TestZ21MotivePowerUnitState(unittest.TestCase):

    def test_construct_loco(self):
        chars = bytes([0x0f, 0x00, 0x40, 0x00, 0xef, 0x00, 0x04, 0x0c, 0xb5, 0x01, 0x00, 0x00, 0x00, 0x00, 0x53])
        obj1 = Dataset.construct_from_bytes(chars)
        obj2 = Z21MotivePowerUnitState.construct_from_dataset(obj1)
        self.assertEqual('MotivePowerUnitState:{address:4, functions:-+------------------------------, '
                         'is_busy:True, stepping:STEPS_128, speed_value:53, reverse:False, '
                         'double_traction:False, smart_search:False}', str(obj2))


    def test_construct_x_dataset(self):
        chars = bytes([0x0f, 0x00, 0x40, 0x00, 0xef, 0x00, 0x04, 0x0c, 0xb5, 0x01, 0x00, 0x00, 0x00, 0x00, 0x53])
        obj1 = Dataset.construct_from_bytes(chars)
        obj2 = Z21MotivePowerUnitState.construct_from_dataset(obj1)
        self.assertEqual(False, obj2.is_emergency_stop)
