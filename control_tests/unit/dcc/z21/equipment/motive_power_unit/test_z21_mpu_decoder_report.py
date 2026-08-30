"""
Created on 1 Jul 2026

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v unit/dcc/z21/entities/motive_power_unit/test_z21_mpu_decoder_report.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import unittest


# --------------------------------------------------------------------------------------------------------------------

class TestZ21MPUDecoderReport(unittest.TestCase):
    pass

    # TODO: implement tests

    # def test_construct(self):
    #     chars = bytes([0x0f, 0x00, 0x40, 0x00, 0xef, 0x00, 0x04, 0x0c, 0xb5, 0x01, 0x00, 0x00, 0x00, 0x00, 0x53])
    #     obj1 = Dataset.construct_from_bytes(chars)
    #     obj2 = Z21MPUDecoderReport.construct_from_dataset(obj1)
    #     self.assertEqual('MPUConfigurationReport:{address:4, functions:-+------------------------------, '
    #                      'is_busy:True, stepping:STEPS_128, speed_setting:53, reverse:False, '
    #                      'double_traction:False, smart_search:False}', str(obj2))


# --------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
