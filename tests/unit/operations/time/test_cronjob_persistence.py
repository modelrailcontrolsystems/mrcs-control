"""
Created on 1 Jan 2026

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v operations/message/test_cronjob_persistence.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import time
import unittest

from mrcs_control.operations.time.persistent_cronjob import PersistentCronjob

from mrcs_core.data.equipment_identity import EquipmentIdentifier, EquipmentType
from mrcs_core.data.iso_datetime import ISODatetime

from setup import Setup


# --------------------------------------------------------------------------------------------------------------------

class TestCronjobPersistence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Setup.dbSetup()


    def test_recreate_tables(self):
        PersistentCronjob.recreate_tables()

        job = PersistentCronjob.find_next()
        self.assertIsNone(job)


    def test_insert(self):
        PersistentCronjob.recreate_tables()

        source = EquipmentIdentifier(EquipmentType.SCH, None, 1)
        job = PersistentCronjob(None, source, 'abc', ISODatetime.now())
        id = job.save()
        self.assertEqual(id, 1)


    def test_find(self):
        PersistentCronjob.recreate_tables()

        source = EquipmentIdentifier(EquipmentType.SCH, None, 1)
        job1 = PersistentCronjob(None, source, 'abc', ISODatetime.now())
        job1.save()
        time.sleep(1)

        source = EquipmentIdentifier(EquipmentType.SCH, None, 1)
        job2 = PersistentCronjob(None, source, 'abd', ISODatetime.now())
        job2.save()
        time.sleep(1)

        job = PersistentCronjob.find_next()
        self.assertEqual(job, job1)


    def test_delete(self):
        PersistentCronjob.recreate_tables()

        source = EquipmentIdentifier(EquipmentType.SCH, None, 1)
        job1 = PersistentCronjob(None, source, 'abc', ISODatetime.now())
        job1.save()
        time.sleep(1)

        source = EquipmentIdentifier(EquipmentType.SCH, None, 1)
        job2 = PersistentCronjob(None, source, 'abd', ISODatetime.now())
        job2.save()
        time.sleep(1)

        job = PersistentCronjob.find_next()
        self.assertEqual(job, job1)

        PersistentCronjob.delete(job.id)

        job = PersistentCronjob.find_next()
        self.assertEqual(job, job2)


if __name__ == "__main_":
    unittest.main()
