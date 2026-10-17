"""
Created on 6 Jul 2026

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v unit/equipment/turnout/test_turnout_persistence.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import json
import sqlite3
import unittest
from pathlib import Path

from mrcs_control.db.db_client import DbClient, DbMode
from mrcs_control.equipment.block.persistent_block_status import PersistentBlockStatus
from mrcs_control.equipment.turnout.persistent_turnout_status import PersistentTurnoutStatus
from mrcs_control.test.test_helper import TestHelper
from mrcs_core.equipment.turnout.turnout_enums import TurnoutPosition
from mrcs_core.equipment.turnout.turnout_report import TurnoutReport
from mrcs_core.equipment.turnout.turnout_status import TurnoutStatus
from mrcs_core.layout.layout import Layout


# --------------------------------------------------------------------------------------------------------------------

class TestTurnoutPersistence(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        DbClient.set_client_db_mode(DbMode.TEST)
        TestHelper.dbSetup()
        cls.__setup_db()


    @classmethod
    def tearDownClass(cls):
        cls.__setup_db()
        TestHelper.dbTeardown()


    @classmethod
    def __setup_db(cls):
        # turnouts reference blocks, so the block table must be built and populated first
        PersistentBlockStatus.recreate_tables()
        PersistentTurnoutStatus.recreate_tables()

        abs_filename = Path(__file__).parent / 'data' / 'test_001_layout.json'
        with open(abs_filename) as fp:
            jdict = json.load(fp)

        layout = Layout.construct_from_jdict(jdict)

        for block in layout.block_abstract().items:
            PersistentBlockStatus.narrow(block).save()

        for turnout in layout.turnout_abstract().items:
            PersistentTurnoutStatus.narrow(turnout).save()


    def __find(self, label: str) -> PersistentTurnoutStatus:
        obj = PersistentTurnoutStatus.find(label)
        if obj is None:
            self.fail(f'turnout {label} not found')

        return obj


    # ----------------------------------------------------------------------------------------------------------------
    # each test resets the tables, so that tests that modify the DB do not affect those that follow

    def test_setup(self):
        self.__setup_db()
        objs = PersistentTurnoutStatus.find_all()
        self.assertEqual(4, len(objs))


    def test_find_all_order(self):
        self.__setup_db()
        labels = [(obj.block_label, obj.label) for obj in PersistentTurnoutStatus.find_all()]
        self.assertEqual([('BN04', 'TE02'), ('BN06', 'TW02'), ('BS02', 'TE01'), ('BS06', 'TW01')], labels)


    def test_find(self):
        self.__setup_db()
        obj = PersistentTurnoutStatus.find('TE01')
        self.assertEqual('PersistentTurnoutStatus:{label:TE01, block_label:BS02, turnout_address:3, position:UNKNOWN}',
                         str(obj))


    def test_find_not_found(self):
        self.__setup_db()
        obj = PersistentTurnoutStatus.find('junk')
        self.assertIsNone(obj)


    def test_find_by_address(self):
        self.__setup_db()
        obj1 = self.__find('TE01')
        obj2 = PersistentTurnoutStatus.find_by_address(obj1.turnout_address)
        self.assertEqual(obj1, obj2)


    def test_find_by_address_not_found(self):
        self.__setup_db()
        obj = PersistentTurnoutStatus.find_by_address(99)
        self.assertIsNone(obj)


    def test_find_for_block(self):
        self.__setup_db()
        objs = PersistentTurnoutStatus.find_for_block('BS02')
        self.assertEqual(['TE01'], [obj.label for obj in objs])


    def test_find_for_block_order(self):
        self.__setup_db()
        PersistentTurnoutStatus('TE09', 'BS02', 9, TurnoutPosition.P0).save()
        PersistentTurnoutStatus('TE05', 'BS02', 5, TurnoutPosition.P0).save()

        objs = PersistentTurnoutStatus.find_for_block('BS02')
        self.assertEqual(['TE01', 'TE05', 'TE09'], [obj.label for obj in objs])


    def test_find_for_block_empty(self):
        self.__setup_db()
        objs = PersistentTurnoutStatus.find_for_block('BS01')
        self.assertEqual([], objs)


    def test_find_for_block_not_found(self):
        self.__setup_db()
        objs = PersistentTurnoutStatus.find_for_block('junk')
        self.assertEqual([], objs)


    def test_exists(self):
        self.__setup_db()
        exists = PersistentTurnoutStatus.exists('TE01')
        self.assertTrue(exists)


    def test_not_exists(self):
        self.__setup_db()
        exists = PersistentTurnoutStatus.exists('junk')
        self.assertFalse(exists)


    def test_save_new(self):
        self.__setup_db()
        obj1 = PersistentTurnoutStatus('TX01', 'BS01', 9, TurnoutPosition.P1)
        obj1.save()

        obj2 = PersistentTurnoutStatus.find('TX01')
        self.assertEqual(obj1, obj2)
        self.assertEqual(5, len(PersistentTurnoutStatus.find_all()))


    def test_save_replace(self):
        self.__setup_db()
        obj1 = self.__find('TE01')
        obj2 = PersistentTurnoutStatus(obj1.label, obj1.block_label, obj1.turnout_address, TurnoutPosition.P1)
        obj2.save()

        obj3 = PersistentTurnoutStatus.find('TE01')
        self.assertEqual(obj2, obj3)
        self.assertEqual(4, len(PersistentTurnoutStatus.find_all()))


    def test_save_duplicate_address(self):
        self.__setup_db()
        obj1 = self.__find('TE01')
        obj2 = PersistentTurnoutStatus('TX01', 'BS01', obj1.turnout_address, TurnoutPosition.P0)
        obj2.save()  # REPLACE resolves the UNIQUE address conflict

        self.assertFalse(PersistentTurnoutStatus.exists('TE01'))
        self.assertTrue(PersistentTurnoutStatus.exists('TX01'))


    def test_save_block_not_found(self):
        self.__setup_db()
        obj = PersistentTurnoutStatus('TX01', 'junk', 9, TurnoutPosition.P0)

        with self.assertRaises(sqlite3.IntegrityError):
            obj.save()  # FOREIGN KEY constraint

        self.assertFalse(PersistentTurnoutStatus.exists('TX01'))


    def test_update_from_turnout_report(self):
        self.__setup_db()
        report = TurnoutReport(3, TurnoutPosition.P1)

        obj1 = PersistentTurnoutStatus.update_from_turnout_report(report)
        self.assertEqual('PersistentTurnoutStatus:{label:TE01, block_label:BS02, turnout_address:3, position:P1}',
                         str(obj1))

        obj2 = PersistentTurnoutStatus.find('TE01')
        self.assertEqual(obj1, obj2)


    def test_update_from_turnout_report_others_unchanged(self):
        self.__setup_db()
        PersistentTurnoutStatus.update_from_turnout_report(TurnoutReport(3, TurnoutPosition.P1))

        positions = {obj.label: obj.position for obj in PersistentTurnoutStatus.find_all()}
        self.assertEqual({'TE01': TurnoutPosition.P1, 'TE02': TurnoutPosition.UNKNOWN,
                          'TW01': TurnoutPosition.UNKNOWN, 'TW02': TurnoutPosition.UNKNOWN}, positions)


    def test_update_from_turnout_report_not_found(self):
        self.__setup_db()
        report = TurnoutReport(99, TurnoutPosition.P1)

        with self.assertRaises(KeyError):
            PersistentTurnoutStatus.update_from_turnout_report(report)


    def test_delete(self):
        self.__setup_db()
        PersistentTurnoutStatus.delete('TE01')

        self.assertIsNone(PersistentTurnoutStatus.find('TE01'))
        self.assertEqual(3, len(PersistentTurnoutStatus.find_all()))
        self.assertTrue(PersistentBlockStatus.exists('BS02'))  # the block is not affected


    def test_delete_not_found(self):
        self.__setup_db()
        PersistentTurnoutStatus.delete('junk')
        self.assertEqual(4, len(PersistentTurnoutStatus.find_all()))


    def test_block_delete_cascades(self):
        self.__setup_db()
        PersistentBlockStatus.delete_block('BS02')

        self.assertIsNone(PersistentTurnoutStatus.find('TE01'))
        self.assertEqual(3, len(PersistentTurnoutStatus.find_all()))


    # ----------------------------------------------------------------------------------------------------------------

    def test_narrow(self):
        obj1 = TurnoutStatus('TX01', 'BS01', 9, TurnoutPosition.P1)
        obj2 = PersistentTurnoutStatus.narrow(obj1)
        self.assertIsInstance(obj2, PersistentTurnoutStatus)
        self.assertEqual(obj1, obj2)


    def test_construct_from_db(self):
        obj = PersistentTurnoutStatus.construct_from_db(['TX01', 'BS01', 9, 'P1'])
        self.assertEqual('PersistentTurnoutStatus:{label:TX01, block_label:BS01, turnout_address:9, position:P1}',
                         str(obj))


    def test_as_db_insert(self):
        obj = PersistentTurnoutStatus('TX01', 'BS01', 9, TurnoutPosition.P1)
        self.assertEqual(('TX01', 'BS01', 9, 'P1'), obj.as_db_insert())


    def test_as_db_update(self):
        obj = PersistentTurnoutStatus('TX01', 'BS01', 9, TurnoutPosition.P1)
        with self.assertRaises(NotImplementedError):
            obj.as_db_update()


    def test_type_name(self):
        self.assertEqual('TurnoutStatus', PersistentTurnoutStatus.type_name())


# --------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
