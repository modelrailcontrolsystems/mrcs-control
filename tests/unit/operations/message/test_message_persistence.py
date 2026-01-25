"""
Created on 16 Nov 2025

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v operations/message/test_message_persistence.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import json
import unittest

from mrcs_control.operations.recorder.persistent_message_record import PersistentMessageRecord
from mrcs_control.operations.recorder.persistent_message import PersistentMessage

from setup import Setup


# --------------------------------------------------------------------------------------------------------------------

class TestMessagePersistence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Setup.dbSetup()

    def test_recreate(self):
        PersistentMessageRecord.recreate_tables()

        records = list(PersistentMessageRecord.find_latest(limit=10))
        self.assertEqual(len(records), 0)

    def test_construct(self):
        PersistentMessageRecord.recreate_tables()

        obj1 = PersistentMessage.construct_from_jdict(
            json.loads('{"origin":"12345678", "routing": "TST.001.002.MPU.001.100", "body": "hello"}'))
        obj1.save()

        records = list(PersistentMessageRecord.find_latest(limit=10))
        obj2 = records[0]

        self.assertEqual(obj2.routing_key, obj1.routing_key)
        self.assertEqual(obj2.body, obj1.body)


if __name__ == "__main_":
    unittest.main()
