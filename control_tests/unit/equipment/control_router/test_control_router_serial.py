"""
Created on 9 Aug 2026

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v unit/equipment/control_router/test_control_router_serial.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import unittest

from mrcs_control.equipment.control_router.control_router_identity import ControlRouterSerial


# --------------------------------------------------------------------------------------------------------------------

class TestControlRouterSerial(unittest.TestCase):

    def test_serial_common(self):
        obj1 = ControlRouterSerial.Common
        self.assertEqual('Common{3}', str(obj1))


    def test_serial_unclassified(self):
        obj1 = ControlRouterSerial.Unclassified
        self.assertEqual('Unclassified{2}', str(obj1))


    def test_serial_system(self):
        obj1 = ControlRouterSerial.System
        self.assertEqual('System{4}', str(obj1))


    def test_serial_track(self):
        obj1 = ControlRouterSerial.Track
        self.assertEqual('Track{5}', str(obj1))


    def test_serial_signal(self):
        obj1 = ControlRouterSerial.Signal
        self.assertEqual('Signal{6}', str(obj1))


    def test_serial_mpu(self):
        obj1 = ControlRouterSerial.MPU
        self.assertEqual('MPU{7}', str(obj1))
