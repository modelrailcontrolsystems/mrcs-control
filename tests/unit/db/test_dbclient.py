"""
Created on 15 Nov 2025

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v db/test_db.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import unittest

from mrcs_control.db.dbclient import DBClient

from setup import Setup


# --------------------------------------------------------------------------------------------------------------------

class TestDB(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Setup.dbSetup()

    def test_instance(self):
        obj1 = DBClient.instance('Test')
        self.assertEqual('Test', obj1.db_name)
        self.assertIsNotNone(obj1.connection)
        self.assertIsNotNone(obj1.cursor)

    def test_drop_all(self):
        obj1 = DBClient.instance('Test')
        DBClient.kill_all()
        self.assertEqual('Test', obj1.db_name)
        self.assertIsNone(obj1.connection)
        self.assertIsNone(obj1.cursor)

    def test_str(self):
        obj1 = DBClient.instance('Test')
        DBClient.kill_all()
        self.assertEqual('DBClient:{db_mode:test, db_name:Test, connection:None, cursor:None}', str(obj1))


if __name__ == "__main_":
    unittest.main()
