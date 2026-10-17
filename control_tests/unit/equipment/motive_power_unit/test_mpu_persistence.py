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
from mrcs_core.equipment.motive_power_unit.mpu_enums import MPUDirection, ThrottleSteps
from mrcs_core.equipment.motive_power_unit.mpu_functions import MPUFunctions
from mrcs_core.equipment.motive_power_unit.mpu_status import MPUStatus
from mrcs_core.inventory.inventory import Inventory


# --------------------------------------------------------------------------------------------------------------------

class TestMPUPersistence(unittest.TestCase):

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
        PersistentMPUStatus.recreate_tables()

        abs_filename = Path(__file__).parent / 'data' / 'test_001_inventory.json'
        with open(abs_filename) as fp:
            jdict = json.load(fp)

        inventory = Inventory.construct_from_jdict(jdict)

        for mpu in inventory.mpu_abstract().items:
            PersistentMPUStatus.narrow(mpu).save()


    def __find(self, label: str) -> PersistentMPUStatus:
        obj = PersistentMPUStatus.find(label)
        if obj is None:
            self.fail(f'mpu {label} not found')

        return obj


    @classmethod
    def __save_mpu(cls, label: str, mpu_address: int) -> PersistentMPUStatus:
        obj = PersistentMPUStatus(label, mpu_address, MPUFunctions.construct_from_jdict('+-+'), 12, 7,
                                  MPUDirection.FORWARD)
        obj.save()

        return obj


    # ----------------------------------------------------------------------------------------------------------------
    # each test resets the tables, so that tests that modify the DB do not affect those that follow

    def test_setup(self):
        self.__setup_db()
        objs = PersistentMPUStatus.find_all()
        self.assertEqual(1, len(objs))


    def test_find_all_order(self):
        self.__setup_db()
        self.__save_mpu('CL60', 4)
        self.__save_mpu('AL01', 3)

        labels = [obj.label for obj in PersistentMPUStatus.find_all()]
        self.assertEqual(['AL01', 'CL60', 'DB59'], labels)


    def test_find_addresses(self):
        self.__setup_db()
        self.__save_mpu('CL60', 4)
        self.__save_mpu('AL01', 3)

        addresses = PersistentMPUStatus.find_addresses()
        self.assertEqual([3, 4, 5], addresses)


    def test_find_addresses_empty(self):
        PersistentMPUStatus.recreate_tables()
        addresses = PersistentMPUStatus.find_addresses()
        self.assertEqual([], addresses)


    def test_find(self):
        self.__setup_db()
        obj = PersistentMPUStatus.find('DB59')
        self.assertEqual('PersistentMPUStatus:{label:DB59, mpu_address:5, functions:, speed_setting:None, speed:None, '
                         'direction:UNKNOWN{2}}', str(obj))


    def test_find_not_found(self):
        self.__setup_db()
        obj = PersistentMPUStatus.find('junk')
        self.assertIsNone(obj)


    def test_find_by_address(self):
        self.__setup_db()
        obj1 = self.__find('DB59')
        obj2 = PersistentMPUStatus.find_by_address(obj1.mpu_address)
        self.assertEqual(obj1, obj2)


    def test_find_by_address_not_found(self):
        self.__setup_db()
        obj = PersistentMPUStatus.find_by_address(99)
        self.assertIsNone(obj)


    def test_exists(self):
        self.__setup_db()
        exists = PersistentMPUStatus.exists('DB59')
        self.assertTrue(exists)


    def test_not_exists(self):
        self.__setup_db()
        exists = PersistentMPUStatus.exists('junk')
        self.assertFalse(exists)


    def test_save_new(self):
        self.__setup_db()
        obj1 = self.__save_mpu('CL60', 4)

        obj2 = PersistentMPUStatus.find('CL60')
        self.assertEqual(obj1, obj2)
        self.assertEqual(2, len(PersistentMPUStatus.find_all()))


    def test_save_replace(self):
        self.__setup_db()
        obj1 = self.__find('DB59')
        obj2 = PersistentMPUStatus(obj1.label, obj1.mpu_address, MPUFunctions.construct_from_jdict('++-'), 20, 15,
                                   MPUDirection.REVERSE)
        obj2.save()

        obj3 = PersistentMPUStatus.find('DB59')
        self.assertEqual(obj2, obj3)
        self.assertEqual(1, len(PersistentMPUStatus.find_all()))


    def test_save_duplicate_address(self):
        self.__setup_db()
        obj1 = self.__find('DB59')
        self.__save_mpu('CL60', obj1.mpu_address)      # REPLACE resolves the UNIQUE address conflict

        self.assertFalse(PersistentMPUStatus.exists('DB59'))
        self.assertTrue(PersistentMPUStatus.exists('CL60'))


    def test_update_from_configuration_report(self):
        self.__setup_db()
        report = MPUConfigurationReport(5, MPUFunctions.construct_from_jdict('+-+'), False, ThrottleSteps.STEPS_28,
                                        12, True, False, True)

        obj1 = PersistentMPUStatus.update_from_configuration_report(report)
        self.assertEqual('PersistentMPUStatus:{label:DB59, mpu_address:5, functions:+-+, speed_setting:12, '
                         'speed:None, direction:REVERSE{1}}', str(obj1))

        obj2 = PersistentMPUStatus.find('DB59')
        self.assertEqual(obj1, obj2)


    def test_update_from_configuration_report_forward(self):
        self.__setup_db()
        report = MPUConfigurationReport(5, MPUFunctions.construct_from_jdict('+-+'), False, ThrottleSteps.STEPS_28,
                                        12, False, False, True)

        obj = PersistentMPUStatus.update_from_configuration_report(report)
        self.assertEqual(MPUDirection.FORWARD, obj.direction)


    def test_update_from_configuration_report_preserves_speed(self):
        self.__setup_db()
        obj1 = self.__save_mpu('CL60', 4)
        report = MPUConfigurationReport(4, MPUFunctions.construct_from_jdict('---'), False, ThrottleSteps.STEPS_28,
                                        20, True, False, True)

        obj2 = PersistentMPUStatus.update_from_configuration_report(report)
        self.assertEqual(obj1.speed, obj2.speed)


    def test_update_from_configuration_report_not_found(self):
        self.__setup_db()
        report = MPUConfigurationReport(99, MPUFunctions.construct_from_jdict('+-+'), False, ThrottleSteps.STEPS_28,
                                        12, True, False, True)

        with self.assertRaises(KeyError):
            PersistentMPUStatus.update_from_configuration_report(report)


    def test_update_from_decoder_report(self):
        self.__setup_db()
        report = MPUDecoderReport(5, 456, 789, 171, 90, 5)

        obj1 = PersistentMPUStatus.update_from_decoder_report(report)
        self.assertEqual('PersistentMPUStatus:{label:DB59, mpu_address:5, functions:, speed_setting:None, speed:90, '
                         'direction:UNKNOWN{2}}', str(obj1))

        obj2 = PersistentMPUStatus.find('DB59')
        self.assertEqual(obj1, obj2)


    def test_update_from_decoder_report_preserves_configuration(self):
        self.__setup_db()
        obj1 = self.__save_mpu('CL60', 4)
        report = MPUDecoderReport(4, 456, 789, 171, 90, 5)

        obj2 = PersistentMPUStatus.update_from_decoder_report(report)
        self.assertEqual(obj1.functions, obj2.functions)
        self.assertEqual(obj1.speed_setting, obj2.speed_setting)
        self.assertEqual(obj1.direction, obj2.direction)


    def test_update_from_decoder_report_not_found(self):
        self.__setup_db()
        report = MPUDecoderReport(99, 456, 789, 171, 90, 5)

        with self.assertRaises(KeyError):
            PersistentMPUStatus.update_from_decoder_report(report)


    def test_delete(self):
        self.__setup_db()
        self.__save_mpu('CL60', 4)
        PersistentMPUStatus.delete('DB59')

        self.assertIsNone(PersistentMPUStatus.find('DB59'))
        self.assertEqual(['CL60'], [obj.label for obj in PersistentMPUStatus.find_all()])


    def test_delete_not_found(self):
        self.__setup_db()
        PersistentMPUStatus.delete('junk')
        self.assertEqual(1, len(PersistentMPUStatus.find_all()))


    # ----------------------------------------------------------------------------------------------------------------

    def test_narrow(self):
        obj1 = MPUStatus('CL60', 4, MPUFunctions.construct_from_jdict('+-+'), 12, 7, MPUDirection.FORWARD)
        obj2 = PersistentMPUStatus.narrow(obj1)
        self.assertIsInstance(obj2, PersistentMPUStatus)
        self.assertEqual(obj1, obj2)


    def test_construct_from_db(self):
        obj = PersistentMPUStatus.construct_from_db(['CL60', 4, '+-+', 12, 7, 'FORWARD'])
        self.assertEqual('PersistentMPUStatus:{label:CL60, mpu_address:4, functions:+-+, speed_setting:12, speed:7, '
                         'direction:FORWARD{0}}', str(obj))


    def test_construct_from_db_nulls(self):
        obj = PersistentMPUStatus.construct_from_db(['CL60', 4, '', None, None, 'UNKNOWN'])
        self.assertEqual([], obj.functions.funcs)
        self.assertIsNone(obj.speed_setting)
        self.assertIsNone(obj.speed)


    def test_as_db_insert(self):
        obj = PersistentMPUStatus('CL60', 4, MPUFunctions.construct_from_jdict('+-+'), 12, 7, MPUDirection.FORWARD)
        self.assertEqual(('CL60', 4, '+-+', 12, 7, 'FORWARD'), obj.as_db_insert())


    def test_as_db_update(self):
        obj = PersistentMPUStatus('CL60', 4, MPUFunctions.construct_from_jdict('+-+'), 12, 7, MPUDirection.FORWARD)
        with self.assertRaises(NotImplementedError):
            obj.as_db_update()


    def test_type_name(self):
        self.assertEqual('MPUStatus', PersistentMPUStatus.type_name())


# --------------------------------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
