"""
Created on 5 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v dcc/z21/command/test_header.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import unittest

from mrcs_control.dcc.z21.command.header import Header, XHeader


# --------------------------------------------------------------------------------------------------------------------

class TestHeader(unittest.TestCase):

    def test_header(self):
        obj1 = Header(0xe8)
        self.assertEqual('LAN_ZLINK_GET_HWINFO', obj1.name)
        self.assertEqual(0xe8, obj1.value)


    def test_header_construct(self):
        obj1 = Header.construct(0xDB)
        self.assertEqual('LAN_DECODER_SYSTEMSTATE_GETDATA', obj1.name)
        self.assertEqual(0xDB, obj1.value)


    def test_header_construct_bad(self):
        obj1 = Header.construct(0xff)
        self.assertEqual('LAN_UNKNOWN', obj1.name)
        self.assertEqual(0x00, obj1.value)


    def test_x_header(self):
        obj1 = XHeader(0xf3)
        self.assertEqual('LAN_X_GET_FIRMWARE_VERSION_REPLY', obj1.name)
        self.assertEqual(0xf3, obj1.value)


    def test_x_header_construct(self):
        obj1 = XHeader.construct(0xf1)
        self.assertEqual('LAN_X_GET_FIRMWARE_VERSION', obj1.name)
        self.assertEqual(0xf1, obj1.value)


    def test_x_header_construct_bad(self):
        obj1 = XHeader.construct(0xff)
        self.assertEqual('LAN_X_UNKNOWN', obj1.name)
        self.assertEqual(0x00, obj1.value)


    if __name__ == "__main__":
        unittest.main()
