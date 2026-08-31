"""
Created on 22 Aug 2026

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v unit/dcc/z21/command/test_command_high_level.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import unittest

from mrcs_control.dcc.z21.command.command import Command, XCommand
from mrcs_control.dcc.z21.command.station import Station
from mrcs_core.equipment.motive_power_unit.mpu_enums import MPUDirection
from mrcs_core.equipment.track.track_enums import TrackMode
from mrcs_core.equipment.turnout.turnout_enums import TurnoutPosition


# --------------------------------------------------------------------------------------------------------------------

class TestCommandBuilders(unittest.TestCase):

    def test_lan_set_broadcast_flags(self):
        obj1 = Command.lan_set_broadcast_flags(Station.default_conf().subscription)
        self.assertEqual('Command:{header:LAN_SET_BROADCAST_FLAGS, argv:[0xd0001]}', str(obj1))


    def test_lan_system_get_data(self):
        obj1 = Command.lan_system_get_data()
        self.assertEqual('Command:{header:LAN_SYSTEM_GET_DATA, argv:[]}', str(obj1))


    def test_lan_railcom_get_data(self):
        obj1 = Command.lan_railcom_get_data(1)
        self.assertEqual('Command:{header:LAN_RAILCOM_GET_DATA, argv:[0x1, 0x1]}', str(obj1))


    def test_lan_log_off(self):
        obj1 = Command.lan_log_off()
        self.assertEqual('Command:{header:LAN_LOG_OFF, argv:[]}', str(obj1))


    # ----------------------------------------------------------------------------------------------------------------

    def test_lan_x_set_track_power(self):
        obj1 = XCommand.lan_x_set_track_power(TrackMode.COMMAND_POWER_ON)
        self.assertEqual('XCommand:{header:LAN_X, x_header:LAN_X_SET_TRACK_POWER, argv:[COMMAND_POWER_ON{0x81}]}',
                         str(obj1))


    def test_lan_x_set_turnout(self):
        obj1 = XCommand.lan_x_set_turnout(1, TurnoutPosition.P1)
        self.assertEqual('XCommand:{header:LAN_X, x_header:LAN_X_SET_TURNOUT, argv:[0x0, 0xa9]}', str(obj1))


    def test_lan_x_get_mpu(self):
        obj1 = XCommand.lan_x_get_mpu(1)
        self.assertEqual('XCommand:{header:LAN_X, x_header:LAN_X_GET_LOCO, argv:[0xf0, 0x1]}', str(obj1))


    def test_lan_x_set_mpu_func(self):
        obj1 = XCommand.lan_x_set_mpu_func(1, MPUDirection.FORWARD, 34)
        self.assertEqual('XCommand:{header:LAN_X, x_header:LAN_X_SET_LOCO_FUNC, argv:[0x13, 0x1, 0x22]}', str(obj1))


# --------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
