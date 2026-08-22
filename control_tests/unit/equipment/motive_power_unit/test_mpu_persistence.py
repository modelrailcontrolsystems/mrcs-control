"""
Created on 29 Nov 2025

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v unit/equipment/motive_power_unit/test_mpu_persistence.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import json
import unittest
from pathlib import Path

from mrcs_control.db.db_client import DbClient, DbMode
from mrcs_control.equipment.motive_power_unit.persistent_mpu_status import PersistentMPUStatus
from mrcs_control.test.test_helper import TestHelper
from mrcs_core.equipment.motive_power_unit.mpu_configuration_report import MPUConfigurationReport
from mrcs_core.equipment.motive_power_unit.mpu_decoder_report import MPUDecoderReport


# --------------------------------------------------------------------------------------------------------------------

class TestMPUPersistence(unittest.TestCase):


    @classmethod
    def setUpClass(cls):
        DbClient.set_client_db_mode(DbMode.TEST)
        TestHelper.dbSetup()


    @classmethod
    def tearDownClass(cls):
        TestHelper.dbTeardown()


    def test_setup(self):
        obj1, obj2 = self.__setup_db()
        self.assertEqual('PersistentMPUStatus:{label:EMR Class 08, mpu_address:3, functions:+-+, '
                         'speed_setting:12, speed:7, reverse:True}', str(obj1))
        self.assertEqual('PersistentMPUStatus:{label:DB Class 60, mpu_address:4, functions:+-+, '
                         'speed_setting:15, speed:8, reverse:False}', str(obj2))


    def test_find(self):
        obj1, _ = self.__setup_db()
        obj2 = PersistentMPUStatus.find(obj1.label)
        self.assertEqual(obj1, obj2)


    def test_find_by_addr(self):
        obj1, _ = self.__setup_db()
        obj2 = PersistentMPUStatus.find_by_address(obj1.mpu_address)
        self.assertEqual(obj1, obj2)


    def test_find_all(self):
        self.__setup_db()
        objs = PersistentMPUStatus.find_all()
        self.assertEqual(2, len(objs))


    def test_exists(self):
        obj1, _ = self.__setup_db()
        exists = PersistentMPUStatus.exists(obj1.label)
        self.assertTrue(exists)


    def test_not_exists(self):
        self.__setup_db()
        exists = PersistentMPUStatus.exists('junk')
        self.assertFalse(exists)


    def test_update_from_config(self):
        obj1, _ = self.__setup_db()

        abs_filename = Path(__file__).parent / 'data' / 'mpu_config.json'
        with open(abs_filename) as fp:
            jdict = json.load(fp)
        obj2 = MPUConfigurationReport.construct_from_jdict(jdict)

        obj3 = PersistentMPUStatus.update_from_configuration_report(obj2)
        self.assertEqual('PersistentMPUStatus:{label:EMR Class 08, mpu_address:3, functions:-+-, '
                         'speed_setting:99, speed:7, reverse:False}', str(obj3))


    def test_update_from_decoder(self):
        obj1, _ = self.__setup_db()

        abs_filename = Path(__file__).parent / 'data' / 'mpu_decoder.json'
        with open(abs_filename) as fp:
            jdict = json.load(fp)
        obj2 = MPUDecoderReport.construct_from_jdict(jdict)

        obj3 = PersistentMPUStatus.update_from_decoder_report(obj2)
        self.assertEqual('PersistentMPUStatus:{label:EMR Class 08, mpu_address:3, functions:+-+, '
                         'speed_setting:12, speed:90, reverse:True}', str(obj3))


    def test_delete(self):
        _, obj2 = self.__setup_db()
        PersistentMPUStatus.delete(obj2.label)
        obj3 = PersistentMPUStatus.find(obj2.label)

        self.assertEqual(obj3, None)


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def __setup_db(cls):
        PersistentMPUStatus.recreate_tables()

        abs_filename = Path(__file__).parent / 'data' / 'mpu_status_1.json'
        with open(abs_filename) as fp:
            jdict = json.load(fp)
        obj1 = PersistentMPUStatus.construct_from_jdict(jdict)
        obj1.save()

        abs_filename = Path(__file__).parent / 'data' / 'mpu_status_2.json'
        with open(abs_filename) as fp:
            jdict = json.load(fp)
        obj2 = PersistentMPUStatus.construct_from_jdict(jdict)
        obj2.save()

        return obj1, obj2


# --------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
