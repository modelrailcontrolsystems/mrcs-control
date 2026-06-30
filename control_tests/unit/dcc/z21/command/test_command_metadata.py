"""
Created on 28 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v unit/dcc/z21/command/test_command_metadata.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import unittest

from mrcs_control.dcc.z21.command import CommandMetadata, XCommandMetadata
from mrcs_control.dcc.z21.command.header import Header, XHeader


# --------------------------------------------------------------------------------------------------------------------

class TestCommandMetadata(unittest.TestCase):

    def test_is_supported(self):
        supported = CommandMetadata.is_supported(Header.LAN_SYSTEMSTATE_GETDATA)
        self.assertTrue(supported)


    def test_is_not_supported(self):
        supported = CommandMetadata.is_supported(Header.LAN_LOCONET_Z21_RX)
        self.assertFalse(supported)


    def test_found(self):
        obj1 = CommandMetadata.find(Header.LAN_SET_BROADCAST_FLAGS)
        self.assertEqual('CommandMetadata:{header:LAN_SET_BROADCAST_FLAGS, data_format:, report_type:None}',
                         str(obj1))


    def test_not_found(self):
        with self.assertRaises(TypeError):
            CommandMetadata.find(Header.LAN_RMBUS_PROGRAMMODULE)


    def test_x_found(self):
        obj1 = XCommandMetadata.find(XHeader.LAN_X_SET_TRACK_POWER)
        self.assertEqual('XCommandMetadata:{header:LAN_X, x_header:LAN_X_SET_TRACK_POWER, data_format:B, '
                         'report_type:TrackState}', str(obj1))


# --------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
