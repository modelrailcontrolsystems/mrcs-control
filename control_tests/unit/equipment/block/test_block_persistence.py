"""
Created on 29 Nov 2025

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v unit/admin/user/test_user_persistence.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import json
import unittest
from pathlib import Path

from mrcs_control.db.db_client import DbClient, DbMode
from mrcs_control.equipment.block.persistent_block_status import PersistentBlockStatus
from mrcs_control.equipment.turnout.persistent_turnout_status import PersistentTurnoutStatus
from mrcs_core.equipment.block.block_report import BlockVoltageReport
from setup import Setup


# --------------------------------------------------------------------------------------------------------------------

class TestBlockPersistence(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        DbClient.set_client_db_mode(DbMode.TEST)
        Setup.dbSetup()


    def test_setup(self):
        obj1, obj2 = self.__setup_db()
        self.assertEqual('BlockStatus:{label:BN01, block_address:5/6, direction:UP, '
                         'voltage:OCCUPIED_WITH_VOLTAGE, '
                         'occupants:[BlockOccupant:{mpu_address:4660, face:FWD}, '
                         'BlockOccupant:{mpu_address:17767, face:REV}]}', str(obj1))
        self.assertEqual('BlockStatus:{label:BN02, block_address:5/7, direction:UP, '
                         'voltage:OCCUPIED_NO_VOLTAGE, '
                         'occupants:[BlockOccupant:{mpu_address:1767, face:REV}, '
                         'BlockOccupant:{mpu_address:4660, face:FWD}]}', str(obj2))


    def test_find(self):
        obj1, _ = self.__setup_db()
        obj2 = PersistentBlockStatus.find(obj1.label)
        self.assertEqual(obj1, obj2)


    def test_find_turnouts(self):
        obj1, _ = self.__setup_db()
        obj2 = PersistentBlockStatus.find(obj1.label)
        assert obj2 is not None
        turnouts = obj2.turnouts
        self.assertEqual(2, len(turnouts))


    def test_find_with_no_occupants(self):
        obj1, _ = self.__setup_db()

        abs_filename = Path(__file__).parent / 'data' / 'block_status_3.json'
        with open(abs_filename) as fp:
            jdict = json.load(fp)
        obj2 = PersistentBlockStatus.construct_from_jdict(jdict)
        obj2.save()

        obj3 = PersistentBlockStatus.find(obj1.label)

        self.assertEqual(2, len(obj1.occupants))
        assert obj3 is not None

        self.assertEqual(0, len(obj3.occupants))


    def test_find_all(self):
        self.__setup_db()
        objs = PersistentBlockStatus.find_all()
        self.assertEqual(2, len(objs))


    def test_exists(self):
        obj1, _ = self.__setup_db()
        exists = PersistentBlockStatus.exists(obj1.label)
        self.assertTrue(exists)


    def test_not_exists(self):
        self.__setup_db()
        exists = PersistentBlockStatus.exists('junk')
        self.assertFalse(exists)


    def test_update(self):
        obj1, _ = self.__setup_db()

        abs_filename = Path(__file__).parent / 'data' / 'block_voltage_report.json'
        with open(abs_filename) as fp:
            jdict = json.load(fp)
        obj2 = BlockVoltageReport.construct_from_jdict(jdict)
        obj3 = obj1.update_from_voltage(obj2)
        self.assertEqual('BlockStatus:{label:BN01, block_address:5/6, direction:UP, '
                         'voltage:FREE_NO_VOLTAGE, '
                         'occupants:[BlockOccupant:{mpu_address:4660, face:FWD}, '
                         'BlockOccupant:{mpu_address:17767, face:REV}]}',
                         str(obj3))


    def test_delete(self):
        _, obj2 = self.__setup_db()
        PersistentBlockStatus.delete(obj2.label)
        obj3 = PersistentBlockStatus.find(obj2.label)

        self.assertEqual(obj3, None)


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def __setup_db(cls):
        PersistentBlockStatus.recreate_tables()

        abs_filename = Path(__file__).parent / 'data' / 'block_status_1.json'
        with open(abs_filename) as fp:
            jdict = json.load(fp)
        obj1 = PersistentBlockStatus.construct_from_jdict(jdict)
        obj1.save()

        abs_filename = Path(__file__).parent / 'data' / 'block_status_2.json'
        with open(abs_filename) as fp:
            jdict = json.load(fp)
        obj2 = PersistentBlockStatus.construct_from_jdict(jdict)
        obj2.save()

        abs_filename = Path(__file__).parent / 'data' / 'turnout_status_1.json'
        with open(abs_filename) as fp:
            jdict = json.load(fp)
        obj3 = PersistentTurnoutStatus.construct_from_jdict(jdict)
        obj3.save()

        abs_filename = Path(__file__).parent / 'data' / 'turnout_status_2.json'
        with open(abs_filename) as fp:
            jdict = json.load(fp)
        obj4 = PersistentTurnoutStatus.construct_from_jdict(jdict)
        obj4.save()

        return obj1, obj2


# --------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
