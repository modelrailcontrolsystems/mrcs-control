"""
Created on 15 Nov 2026

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v unit/equipment/alert/test_alert_persistence.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import unittest

from mrcs_control.equipment.alert.persistent_alert import PersistentAlert
from mrcs_control.test.test_helper import TestHelper
from mrcs_core.data.iso_datetime import ISODatetime
from mrcs_core.equipment.alert.alert import Alert
from mrcs_core.equipment.alert.alert_enums import Impact, Severity, Subject


# --------------------------------------------------------------------------------------------------------------------

class TestAlertPersistence(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        TestHelper.dbSetup()


    @classmethod
    def tearDownClass(cls):
        TestHelper.dbTeardown()


    @classmethod
    def __sample_alert(cls):
        raised_at = ISODatetime.construct_from_jdict('2026-11-15T08:43:56.970+00:00')
        return Alert(None, Severity.HIGH, Impact.GLOBAL, Subject.TRACK, 'short happened', raised_at, None)


    # ----------------------------------------------------------------------------------------------------------------

    def test_narrow(self):
        obj1 = PersistentAlert.narrow(self.__sample_alert())
        self.assertEqual('PersistentAlert:{id:None, severity:HIGH{0}, impact:GLOBAL, subject:TRACK, '
                         'text:short happened, raised_at:ISODatetime:{2026-11-15T08:43:56.970+00:00}, '
                         'resolved_at:None}', str(obj1))


    def test_recreate(self):
        PersistentAlert.recreate_tables()

        records = list(PersistentAlert.find_latest(limit=10))
        self.assertEqual(len(records), 0)


    def test_find_latest(self):
        PersistentAlert.recreate_tables()
        obj1 = PersistentAlert.narrow(self.__sample_alert())
        obj1.save()

        records = list(PersistentAlert.find_latest(limit=10))
        self.assertEqual(1, len(records))
        self.assertEqual('PersistentAlert:{id:1, severity:HIGH{0}, impact:GLOBAL, subject:TRACK, '
                         'text:short happened, raised_at:ISODatetime:{2026-11-15T08:43:56.970+00:00}, '
                         'resolved_at:None}', str(records[0]))


    def test_find_unresolved(self):
        PersistentAlert.recreate_tables()
        obj1 = PersistentAlert.narrow(self.__sample_alert())
        obj1.save()

        records = list(PersistentAlert.find_unresolved())
        self.assertEqual(1, len(records))
        self.assertEqual('PersistentAlert:{id:1, severity:HIGH{0}, impact:GLOBAL, subject:TRACK, '
                         'text:short happened, raised_at:ISODatetime:{2026-11-15T08:43:56.970+00:00}, '
                         'resolved_at:None}', str(records[0]))


    def test_find_by_id(self):
        PersistentAlert.recreate_tables()
        obj1 = PersistentAlert.narrow(self.__sample_alert())
        obj1.save()

        record = PersistentAlert.find_by_id(1)
        self.assertEqual('PersistentAlert:{id:1, severity:HIGH{0}, impact:GLOBAL, subject:TRACK, '
                         'text:short happened, raised_at:ISODatetime:{2026-11-15T08:43:56.970+00:00}, '
                         'resolved_at:None}', str(record))


    def test_resolve(self):
        self.maxDiff = None

        PersistentAlert.recreate_tables()
        obj1 = PersistentAlert.narrow(self.__sample_alert())
        id = obj1.save()

        obj2 = PersistentAlert.find_by_id(id)
        obj2.resolve()
        obj2.save()

        records = list(PersistentAlert.find_latest(limit=10))
        self.assertEqual(1, len(records))
        self.assertTrue(isinstance(obj2.resolved_at, ISODatetime))

        records = list(PersistentAlert.find_unresolved())
        self.assertEqual(0, len(records))


# --------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
