"""
Created on 15 Nov 2025

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v db/test_db.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import unittest

from mrcs_control.db.db_name import DbName
from mrcs_control.db.db_client import DbClient

from setup import Setup


# --------------------------------------------------------------------------------------------------------------------

class TestDB(unittest.TestCase):
    __DATABASE = DbName.Test


    @classmethod
    def setUpClass(cls):
        Setup.dbSetup()

    def test_instance(self):
        obj1 = DbClient.instance(self.__DATABASE)
        self.assertEqual('Test', obj1.db_name)
        self.assertIsNotNone(obj1.connection)
        self.assertIsNotNone(obj1.cursor)

    def test_drop_all(self):
        obj1 = DbClient.instance(self.__DATABASE)
        DbClient.kill_all()
        self.assertEqual('Test', obj1.db_name)
        self.assertIsNone(obj1.connection)
        self.assertIsNone(obj1.cursor)

    def test_str(self):
        obj1 = DbClient.instance(self.__DATABASE)
        DbClient.kill_all()
        self.assertEqual('DbClient:{db_mode:test, db_name:Test, connection:None, cursor:None}', str(obj1))


if __name__ == "__main_":
    unittest.main()
