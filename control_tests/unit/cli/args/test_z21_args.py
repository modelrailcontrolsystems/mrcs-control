"""
Created on 16 Sep 2026

@author: Bruno Beloff (bbeloff@me.com)
"""

import sys
import unittest
from unittest.mock import patch

from mrcs_control.cli.args.z21_args import Z21Args


# --------------------------------------------------------------------------------------------------------------------

class TestZ21Args(unittest.TestCase):

    def test_set_mpu_drive_forward(self):
        with patch.object(sys, 'argv', ['mrcs_control_z21', '-s', '4', 'FWD', '128']):
            args = Z21Args('test')
            self.assertEqual((4, 'FWD', 128), args.set_mpu_drive)
            self.assertTrue(args.has_command)

            cmd = args.command
            self.assertIsNotNone(cmd)
            self.assertEqual('XCommand:{header:LAN_X, x_header:LAN_X_SET_LOCO_FUNC, argv:[0x13, 0x4, 0x80]}', str(cmd))


    def test_set_mpu_drive_reverse_lowercase(self):
        with patch.object(sys, 'argv', ['mrcs_control_z21', '-s', '12', 'rev', '0']):
            args = Z21Args('test')
            self.assertEqual((12, 'REV', 0), args.set_mpu_drive)
            self.assertTrue(args.has_command)

            cmd = args.command
            self.assertIsNotNone(cmd)
            self.assertEqual('XCommand:{header:LAN_X, x_header:LAN_X_SET_LOCO_FUNC, argv:[0x13, 0xc, 0x0]}', str(cmd))


    def test_set_mpu_drive_max_speed(self):
        with patch.object(sys, 'argv', ['mrcs_control_z21', '-s', '3', 'FWD', '255']):
            args = Z21Args('test')
            self.assertEqual((3, 'FWD', 255), args.set_mpu_drive)
            self.assertEqual('XCommand:{header:LAN_X, x_header:LAN_X_SET_LOCO_FUNC, argv:[0x13, 0x3, 0xff]}',
                             str(args.command))


    def test_set_mpu_drive_invalid_addr(self):
        with patch.object(sys, 'argv', ['mrcs_control_z21', '-s', 'abc', 'FWD', '100']):
            with self.assertRaises(SystemExit):
                Z21Args('test')


    def test_set_mpu_drive_invalid_dir(self):
        with patch.object(sys, 'argv', ['mrcs_control_z21', '-s', '4', 'X', '100']):
            with self.assertRaises(SystemExit):
                Z21Args('test')


    def test_set_mpu_drive_invalid_speed_above_max(self):
        with patch.object(sys, 'argv', ['mrcs_control_z21', '-s', '4', 'FWD', '256']):
            with self.assertRaises(SystemExit):
                Z21Args('test')


    def test_set_mpu_drive_invalid_speed_below_min(self):
        with patch.object(sys, 'argv', ['mrcs_control_z21', '-s', '4', 'FWD', '-1']):
            with self.assertRaises(SystemExit):
                Z21Args('test')


    def test_set_mpu_drive_invalid_speed_non_integer(self):
        with patch.object(sys, 'argv', ['mrcs_control_z21', '-s', '4', 'FWD', 'fast']):
            with self.assertRaises(SystemExit):
                Z21Args('test')


    def test_no_set_mpu_drive(self):
        with patch.object(sys, 'argv', ['mrcs_control_z21', '-m']):
            args = Z21Args('test')
            self.assertIsNone(args.set_mpu_drive)
            self.assertFalse(args.has_command)
            self.assertIsNone(args.command)


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
