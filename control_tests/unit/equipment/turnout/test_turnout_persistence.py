"""
Created on 6 Jul 2026

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v unit/equipment/turnout/test_turnout_persistence.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import json
import unittest
from pathlib import Path

from mrcs_control.db.db_client import DbClient, DbMode
from mrcs_control.equipment.turnout.persistent_turnout_status import PersistentTurnoutStatus
from mrcs_core.equipment.turnout.turnout_report import TurnoutReport
from setup import Setup


# --------------------------------------------------------------------------------------------------------------------

class TestTurnoutPersistence(unittest.TestCase):


    @classmethod
    def setUpClass(cls):
        DbClient.set_client_db_mode(DbMode.TEST)
        Setup.dbSetup()


    def test_setup(self):
        obj1, obj2 = self.__setup_db()
        self.assertEqual('TurnoutStatus:{label:TE01, block_label:BN01, turnout_address:13, position:P0}',
                         str(obj1))
        self.assertEqual('TurnoutStatus:{label:TE02, block_label:BN01, turnout_address:14, position:P0}',
                         str(obj2))


    def test_find(self):
        obj1, _ = self.__setup_db()
        obj2 = PersistentTurnoutStatus.find(obj1.label)
        self.assertEqual(obj1, obj2)


    def test_find_by_addr(self):
        obj1, _ = self.__setup_db()
        obj2 = PersistentTurnoutStatus.find_by_address(obj1.turnout_address)
        self.assertEqual(obj1, obj2)


    def test_find_all(self):
        self.__setup_db()
        objs = PersistentTurnoutStatus.find_all()
        self.assertEqual(2, len(objs))


    def test_find_for_block(self):
        self.__setup_db()
        objs = PersistentTurnoutStatus.find_for_block('BN01')
        self.assertEqual(2, len(objs))


    def test_find_for_block_empty(self):
        self.__setup_db()
        objs = PersistentTurnoutStatus.find_for_block('BN02')
        self.assertEqual(0, len(objs))


    def test_exists(self):
        obj1, _ = self.__setup_db()
        exists = PersistentTurnoutStatus.exists(obj1.label)
        self.assertTrue(exists)


    def test_not_exists(self):
        self.__setup_db()
        exists = PersistentTurnoutStatus.exists('junk')
        self.assertFalse(exists)


    def test_update_from_report(self):
        obj1, _ = self.__setup_db()

        abs_filename = Path(__file__).parent / 'data' / 'turnout_report_13.json'
        with open(abs_filename) as fp:
            jdict = json.load(fp)
        obj2 = TurnoutReport.construct_from_jdict(jdict)

        obj3 = PersistentTurnoutStatus.update_from_turnout_report(obj2)
        self.assertEqual('TurnoutStatus:{label:TE01, block_label:BN01, turnout_address:13, position:P1}',
                         str(obj3))


    def test_update_from_report_not_found(self):
        obj1, _ = self.__setup_db()

        abs_filename = Path(__file__).parent / 'data' / 'turnout_report_15.json'
        with open(abs_filename) as fp:
            jdict = json.load(fp)
        obj2 = TurnoutReport.construct_from_jdict(jdict)

        with self.assertRaises(KeyError):
            PersistentTurnoutStatus.update_from_turnout_report(obj2)


    def test_delete(self):
        _, obj2 = self.__setup_db()
        PersistentTurnoutStatus.delete(obj2.label)
        obj3 = PersistentTurnoutStatus.find(obj2.label)

        self.assertEqual(obj3, None)


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def __setup_db(cls):
        PersistentTurnoutStatus.recreate_tables()

        abs_filename = Path(__file__).parent / 'data' / 'turnout_status_1.json'
        with open(abs_filename) as fp:
            jdict = json.load(fp)
        obj1 = PersistentTurnoutStatus.construct_from_jdict(jdict)
        obj1.save()

        abs_filename = Path(__file__).parent / 'data' / 'turnout_status_2.json'
        with open(abs_filename) as fp:
            jdict = json.load(fp)
        obj2 = PersistentTurnoutStatus.construct_from_jdict(jdict)
        obj2.save()

        return obj1, obj2


# --------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
