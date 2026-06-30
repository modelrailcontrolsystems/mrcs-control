"""
Created on 13 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v unit/dcc/z21/entities/track/test_z21_track_state.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import unittest

from mrcs_control.dcc.z21.command.dataset import Dataset
from mrcs_control.dcc.z21.equipment.track.z21_track_state import Z21TrackState


# --------------------------------------------------------------------------------------------------------------------

class TestZ21TrackState(unittest.TestCase):

    def test_construct_track_on(self):
        chars = bytes([0x07, 0x00, 0x40, 0x00, 0x61, 0x01, 0x60])
        obj1 = Dataset.construct_from_bytes(chars)
        obj2 = Z21TrackState.construct_from_dataset(obj1)
        self.assertEqual('TrackState:{mode:POWER_ON}', str(obj2))


    def test_construct_turnout_p1(self):
        chars = bytes([0x07, 0x00, 0x40, 0x00, 0x61, 0x00, 0x61])
        obj1 = Dataset.construct_from_bytes(chars)
        obj2 = Z21TrackState.construct_from_dataset(obj1)
        self.assertEqual('TrackState:{mode:POWER_OFF}', str(obj2))


# --------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
