"""
Created on 13 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v unit/dcc/z21/entities/track/test_z21_track_state.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import unittest

from mrcs_control.dcc.z21.command.dataset import Dataset
from mrcs_control.dcc.z21.equipment.track.track_report_builder import TrackReportBuilder
from mrcs_core.equipment.error.invalid_request_report import InvalidRequestReport
from mrcs_core.equipment.track.track_enums import TrackMode
from mrcs_core.equipment.track.track_report import TrackReport


# --------------------------------------------------------------------------------------------------------------------

class TestTrackReportBuilder(unittest.TestCase):

    def test_construct_track_on(self):
        chars = bytes([0x07, 0x00, 0x40, 0x00, 0x61, 0x01, 0x60])
        obj1 = Dataset.construct_from_bytes(chars)
        obj2 = TrackReportBuilder.construct_from_dataset(obj1)
        self.assertEqual('TrackReport:{mode:POWER_ON{0x01}}', str(obj2))


    def test_construct_turnout_p1(self):
        chars = bytes([0x07, 0x00, 0x40, 0x00, 0x61, 0x00, 0x61])
        obj1 = Dataset.construct_from_bytes(chars)
        obj2 = TrackReportBuilder.construct_from_dataset(obj1)
        self.assertEqual('TrackReport:{mode:POWER_OFF{0x00}}', str(obj2))


    def test_construct_valid_modes(self):
        for mode in TrackMode:
            with self.subTest(mode=mode):
                obj1 = self.__dataset(mode.value)
                obj2 = TrackReportBuilder.construct_from_dataset(obj1)
                self.assertIsInstance(obj2, TrackReport)
                self.assertEqual(mode, obj2.mode)


    def test_construct_invalid_modes(self):
        valid_codes = {mode.value for mode in TrackMode}

        for code in range(17):
            if code in valid_codes:
                continue

            with self.subTest(code=code):
                obj1 = self.__dataset(code)
                obj2 = TrackReportBuilder.construct_from_dataset(obj1)
                self.assertIsInstance(obj2, InvalidRequestReport)
                self.assertEqual(code, obj2.code)


    def test_construct_invalid_request(self):
        obj1 = self.__dataset(0x03)
        obj2 = TrackReportBuilder.construct_from_dataset(obj1)
        self.assertEqual('InvalidRequestReport:{code:3}', str(obj2))


    # ----------------------------------------------------------------------------------------------------------------

    @staticmethod
    def __dataset(code: int) -> Dataset:
        chars = bytes([0x07, 0x00, 0x40, 0x00, 0x61, code, 0x61 ^ code])
        return Dataset.construct_from_bytes(chars)


# --------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
