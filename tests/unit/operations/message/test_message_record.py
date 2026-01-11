"""
Created on 16 Nov 2025

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v operations/message/message_record.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import json
import unittest

from mrcs_control.operations.recorder.message_record import PersistentMessageRecord

from mrcs_core.data.equipment_identity import EquipmentIdentifier, EquipmentFilter
from mrcs_core.data.iso_datetime import ISODatetime
from mrcs_core.data.json import JSONify
from mrcs_core.messaging.routing_key import PublicationRoutingKey
from mrcs_core.operations.recorder.message_record import MessageRecord


# --------------------------------------------------------------------------------------------------------------------

class TestMessageRecord(unittest.TestCase):
    def test_construct(self):
        self.maxDiff = None

        dt = ISODatetime.construct_from_db('2025-08-26 01:23:45.678')
        source = EquipmentIdentifier.construct_from_jdict('SBO.01.02')
        target = EquipmentFilter.construct_from_jdict('OMP.*.*')
        rk = PublicationRoutingKey(source, target)
        obj1 = MessageRecord(1, dt, rk, 'hello')
        self.assertEqual('MessageRecord:{uid:1, rec:ISODatetime:{2025-08-26T02:23:45.678+01:00}, '
                         'routing_key:PublicationRoutingKey:{source:EquipmentIdentifier:{equipment_type:SBO, '
                         'sector_number:1, serial_number:2}, target:EquipmentFilter:{equipment_type:OMP, '
                         'sector_number:None, serial_number:None}}, body:hello}', str(obj1))

    def test_construct_from_jdict(self):
        self.maxDiff = None

        obj1 = MessageRecord.construct_from_jdict(json.loads('{"uid": 1, "rec": "2025-08-26T02:23:45.678+01:00", '
                                                             '"routing": "SBO.001.002.OMP.*.*", "body": "hello"}'))
        self.assertEqual('MessageRecord:{uid:1, rec:ISODatetime:{2025-08-26T02:23:45.678+01:00}, '
                         'routing_key:PublicationRoutingKey:{source:EquipmentIdentifier:{equipment_type:SBO, '
                         'sector_number:1, serial_number:2}, target:EquipmentFilter:{equipment_type:OMP, '
                         'sector_number:None, serial_number:None}}, body:hello}', str(obj1))

    def test_construct_from_db(self):
        self.maxDiff = None

        obj1 = PersistentMessageRecord.construct_from_db(1, '2025-08-26 01:23:45.678',
                                                         'SBO.001.002.OMP.*.*', '"hello"')
        self.assertEqual('PersistentMessageRecord:{uid:1, rec:ISODatetime:{2025-08-26T02:23:45.678+01:00}, '
                         'routing_key:PublicationRoutingKey:{source:EquipmentIdentifier:{equipment_type:SBO, '
                         'sector_number:1, serial_number:2}, target:EquipmentFilter:{equipment_type:OMP, '
                         'sector_number:None, serial_number:None}}, body:hello}', str(obj1))

    def test_eq(self):
        obj1 = MessageRecord.construct_from_jdict(json.loads('{"uid": 1, "rec": "2025-08-26T02:23:45.678+01:00", '
                                                             '"routing": "SBO.001.002.OMP.*.*", "body": "hello"}'))
        obj2 = MessageRecord.construct_from_jdict(json.loads('{"uid": 1, "rec": "2025-08-26T02:23:45.678+01:00", '
                                                             '"routing": "SBO.001.002.OMP.*.*", "body": "hello"}'))
        self.assertEqual(True, obj1 == obj2)

    def test_neq(self):
        obj1 = MessageRecord.construct_from_jdict(json.loads('{"uid": 1, "rec": "2025-08-26T02:23:45.678+01:00", '
                                                             '"routing": "SBO.001.002.OMP.*.*", "body": "hello"}'))
        obj2 = MessageRecord.construct_from_jdict(json.loads('{"uid": 1, "rec": "2025-08-26T02:23:45.678+01:00", '
                                                             '"routing": "SBO.001.002.OMP.*.*", "body": "hello!"}'))
        self.assertEqual(False, obj1 == obj2)

    def test_lt(self):
        obj1 = MessageRecord.construct_from_jdict(json.loads('{"uid": 1, "rec": "2025-08-26T02:23:45.678+01:00", '
                                                             '"routing": "SBO.001.002.OMP.*.*", "body": "hello"}'))
        obj2 = MessageRecord.construct_from_jdict(json.loads('{"uid": 2, "rec": "2025-08-26T02:23:45.678+01:00", '
                                                             '"routing": "SBO.001.002.OMP.*.*", "body": "hello"}'))
        self.assertEqual(True, obj1 < obj2)

    def test_nlt(self):
        obj1 = MessageRecord.construct_from_jdict(json.loads('{"uid": 2, "rec": "2025-08-26T02:23:45.678+01:00", '
                                                             '"routing": "SBO.001.002.OMP.*.*", "body": "hello"}'))
        obj2 = MessageRecord.construct_from_jdict(json.loads('{"uid": 1, "rec": "2025-08-26T02:23:45.678+01:00", '
                                                             '"routing": "SBO.001.002.OMP.*.*", "body": "hello"}'))
        self.assertEqual(False, obj1 < obj2)

    def test_as_json(self):
        obj1 = MessageRecord.construct_from_jdict(json.loads('{"uid": 1, "rec": "2025-08-26T02:23:45.678+01:00", '
                                                             '"routing": "SBO.001.002.OMP.*.*", "body": "hello"}'))
        self.assertEqual('{"uid": 1, "rec": "2025-08-26T02:23:45.678+01:00", "routing": "SBO.001.002.OMP.*.*", '
                         '"body": "hello"}', JSONify.dumps(obj1))


if __name__ == "__main_":
    unittest.main()
