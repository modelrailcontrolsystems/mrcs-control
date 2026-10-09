"""
Created on 7 Oct 2026

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v unit/dcc/z21/equipment/configuration_variable/test_cv_report_builder.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import unittest

from mrcs_control.dcc.z21.command.dataset import Dataset
from mrcs_control.dcc.z21.equipment.configuration_variable.cv_report_builder import CVReportBuilder


# --------------------------------------------------------------------------------------------------------------------

class TestCVReportBuilder(unittest.TestCase):

    def test_construct_cv(self):
        chars = bytes([0x0a, 0x00, 0x40, 0x00, 0x64, 0x14, 0x01, 0x02, 0x03, 0x70])
        obj1 = Dataset.construct_from_bytes(chars)
        obj2 = CVReportBuilder.construct_from_dataset(obj1)
        self.assertEqual('CVReport:{cv_address:259, value:3}', str(obj2))  # 1-based addressing
