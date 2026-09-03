"""
Created on 9 Aug 2026

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v unit/equipment/control_router/test_control_router_serial.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import unittest

from mrcs_control.operations.control_router.control_router_identity import ControlRouterSerial


# --------------------------------------------------------------------------------------------------------------------

class TestControlRouterSerial(unittest.TestCase):

    def test_serial_router(self):
        obj1 = ControlRouterSerial.ROUTER
        self.assertEqual('ROUTER{1}', str(obj1))


    def test_serial_unclassified(self):
        obj1 = ControlRouterSerial.UNCLASSIFIED
        self.assertEqual('UNCLASSIFIED{2}', str(obj1))


    def test_serial_common(self):
        obj1 = ControlRouterSerial.COMMON
        self.assertEqual('COMMON{3}', str(obj1))


    def test_serial_system(self):
        obj1 = ControlRouterSerial.SYSTEM
        self.assertEqual('SYSTEM{4}', str(obj1))


    def test_serial_track(self):
        obj1 = ControlRouterSerial.TRACK
        self.assertEqual('TRACK{5}', str(obj1))


    def test_serial_turnout(self):
        obj1 = ControlRouterSerial.TURNOUT
        self.assertEqual('TURNOUT{6}', str(obj1))


    def test_serial_block(self):
        obj1 = ControlRouterSerial.BLOCK
        self.assertEqual('BLOCK{7}', str(obj1))


    def test_serial_signal(self):
        obj1 = ControlRouterSerial.SIGNAL
        self.assertEqual('SIGNAL{8}', str(obj1))


    def test_serial_mpu(self):
        obj1 = ControlRouterSerial.MPU
        self.assertEqual('MPU{9}', str(obj1))
