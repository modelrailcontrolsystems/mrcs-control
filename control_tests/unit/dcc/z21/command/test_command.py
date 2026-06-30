"""
Created on 25 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v unit/dcc/z21/command/test_command.pypy

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import json
import unittest

from mrcs_control.dcc.z21.command.command import Command, XCommand
from mrcs_control.dcc.z21.command.header import Header, XHeader
from mrcs_core.data.json import JSONify
from mrcs_core.equipment.track.track_mode import TrackMode


# --------------------------------------------------------------------------------------------------------------------

class TestCommand(unittest.TestCase):

    def test_construct(self):
        obj1 = Command.construct(Header.LAN_SYSTEMSTATE_GETDATA)
        self.assertEqual('Command:{header:LAN_SYSTEMSTATE_GETDATA, args:()}', str(obj1))


    def test_dataset(self):
        obj1 = Command.construct(Header.LAN_SYSTEMSTATE_GETDATA)
        obj2 = obj1.dataset
        self.assertEqual('Dataset:{header:0x0085 [LAN_SYSTEMSTATE_GETDATA], total_len:4, data:}', str(obj2))


    def test_x_construct(self):
        obj1 = XCommand.construct(XHeader.LAN_X_SET_TRACK_POWER, TrackMode.COMMAND_POWER_ON)
        self.assertEqual('XCommand:{header:LAN_X, x_header:LAN_X_SET_TRACK_POWER, '
                         'args:[129]}', str(obj1))


    def test_x_dataset(self):
        obj1 = XCommand.construct(XHeader.LAN_X_SET_TRACK_POWER, TrackMode.COMMAND_POWER_ON)
        obj2 = obj1.dataset
        self.assertEqual('XDataset:{header:0x0040 [LAN_X], x_header:0x0021 [LAN_X_SET_TRACK_POWER], '
                         'total_len:7, data:81, xor:0xa0}', str(obj2))


    def test_construct_fail(self):
        with self.assertRaises(TypeError):
            Command.construct(Header.LAN_UNKNOWN)


    def test_json(self):
        obj1 = Command.construct(Header.LAN_SYSTEMSTATE_GETDATA)
        jstr = JSONify.dumps(obj1)
        self.assertEqual('{"type": "Command", "header": "LAN_SYSTEMSTATE_GETDATA", "args": []}', jstr)


    def test_json_eq(self):
        obj1 = XCommand.construct(XHeader.LAN_X_SET_TRACK_POWER, TrackMode.COMMAND_POWER_ON)
        jstr = JSONify.dumps(obj1)
        obj2 = Command.construct_from_jdict(json.loads(jstr))
        self.assertEqual(obj1, obj2)


# --------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
