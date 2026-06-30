"""
Created on 13 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v unit/dcc/z21/entities/control_router/test_z21_control_router_state.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import unittest

from mrcs_control.dcc.z21.command.dataset import Dataset
from mrcs_control.dcc.z21.equipment.control_router.z21_control_router_state import Z21ControlRouterState


# --------------------------------------------------------------------------------------------------------------------

class TestZ21ControlRouterState(unittest.TestCase):

    def test_construct_control_router(self):
        chars = bytes([0x14, 0x00, 0x84, 0x00, 0x0c, 0x01, 0x00, 0x00, 0xce, 0x00, 0x1f, 0x00, 0x1f, 0x4e, 0x14, 0x37,
                       0x00, 0x20, 0x03, 0x79])
        obj1 = Dataset.construct_from_bytes(chars)
        obj2 = Z21ControlRouterState.construct_from_dataset(obj1)
        self.assertEqual('ControlRouterState:{main_current:268, prog_current:0, filtered_main_current:206, '
                         'supply_voltage:19999, track_voltage:14100, temperature:31, central_state:0x00, '
                         'central_state_ext:0x20, capabilities:0x79, reserved:0x03}', str(obj2))


    def test_construct_control_router_is_track_voltage_off(self):
        chars = bytes([0x14, 0x00, 0x84, 0x00, 0x0c, 0x01, 0x00, 0x00, 0xce, 0x00, 0x1f, 0x00, 0x1f, 0x4e, 0x14, 0x37,
                       0x00, 0x20, 0x03, 0x79])
        obj1 = Dataset.construct_from_bytes(chars)
        obj2 = Z21ControlRouterState.construct_from_dataset(obj1)
        self.assertEqual(False, obj2.is_track_voltage_off)


    def test_construct_control_router_is_short_circuit(self):
        chars = bytes([0x14, 0x00, 0x84, 0x00, 0x0c, 0x01, 0x00, 0x00, 0xce, 0x00, 0x1f, 0x00, 0x1f, 0x4e, 0x14, 0x37,
                       0x00, 0x20, 0x03, 0x79])
        obj1 = Dataset.construct_from_bytes(chars)
        obj2 = Z21ControlRouterState.construct_from_dataset(obj1)
        self.assertEqual(False, obj2.is_short_circuit)


    def test_construct_control_router_is_programming_mode(self):
        chars = bytes([0x14, 0x00, 0x84, 0x00, 0x0c, 0x01, 0x00, 0x00, 0xce, 0x00, 0x1f, 0x00, 0x1f, 0x4e, 0x14, 0x37,
                       0x00, 0x20, 0x03, 0x79])
        obj1 = Dataset.construct_from_bytes(chars)
        obj2 = Z21ControlRouterState.construct_from_dataset(obj1)
        self.assertEqual(False, obj2.is_programming_mode)


# --------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
