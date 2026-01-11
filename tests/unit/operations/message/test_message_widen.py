"""
Created on 20 Dec 2025

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v operations/message/message_record.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import unittest

from mrcs_control.operations.recorder.persistent_message import PersistentMessage

from mrcs_core.data.equipment_identity import EquipmentIdentifier, EquipmentFilter
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import PublicationRoutingKey


# --------------------------------------------------------------------------------------------------------------------

class TestMessageWiden(unittest.TestCase):
    def test_construct(self):
        source = EquipmentIdentifier.construct_from_jdict('SBO.01.02')
        target = EquipmentFilter.construct_from_jdict('OMP.*.*')
        rk = PublicationRoutingKey(source, target)
        obj1 = Message(rk, 'hello')
        self.assertEqual('Message:{routing_key:PublicationRoutingKey:'
                         '{source:EquipmentIdentifier:{equipment_type:SBO, sector_number:1, serial_number:2}, '
                         'target:EquipmentFilter:{equipment_type:OMP, sector_number:None, serial_number:None}}, '
                         'body:hello}', str(obj1))

    def test_widen(self):
        source = EquipmentIdentifier.construct_from_jdict('SBO.01.02')
        target = EquipmentFilter.construct_from_jdict('OMP.*.*')
        rk = PublicationRoutingKey(source, target)
        obj1 = Message(rk, 'hello')
        obj2 = PersistentMessage.widen(obj1)
        self.assertEqual('PersistentMessage:{routing_key:PublicationRoutingKey:'
                         '{source:EquipmentIdentifier:{equipment_type:SBO, sector_number:1, serial_number:2}, '
                         'target:EquipmentFilter:{equipment_type:OMP, sector_number:None, serial_number:None}}, '
                         'body:hello}', str(obj2))


if __name__ == "__main_":
    unittest.main()
