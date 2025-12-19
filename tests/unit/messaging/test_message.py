"""
Created on 15 Nov 2025

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v messaging/test_message.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import json
import os
import unittest

from mrcs_control.operations.recorder.message import PersistentMessage

from mrcs_core.data.json import JSONify


# --------------------------------------------------------------------------------------------------------------------

class TestMessage(unittest.TestCase):
    __filename1 = os.path.join(os.path.dirname(__file__), 'data', 'hello.json')
    with open(__filename1) as fp:
        __jdict1 = json.load(fp)

    __filename2 = os.path.join(os.path.dirname(__file__), 'data', 'goodbye.json')
    with open(__filename2) as fp:
        __jdict2 = json.load(fp)

    __filename3 = os.path.join(os.path.dirname(__file__), 'data', 'one_two.json')
    with open(__filename3) as fp:
        __jdict3 = json.load(fp)

    def test_construct_from_jdict(self):
        obj1 = PersistentMessage.construct_from_jdict(self.__jdict1)
        self.assertEqual('PersistentMessage:{routing_key:PublicationRoutingKey:{source:EquipmentIdentifier:'
                         '{equipment_type:TST, sector_number:1, serial_number:2}, '
                         'target:EquipmentFilter:{equipment_type:MPU, sector_number:1, serial_number:100}}, '
                         'body:hello}', str(obj1))

    def test_jdict(self):
        obj1 = PersistentMessage.construct_from_jdict(self.__jdict3)
        self.assertEqual({'routing': 'TST.001.002.MPU.001.100', 'body': (1, 2)}, obj1.as_jdict())

    def test_eq(self):
        obj1 = PersistentMessage.construct_from_jdict(self.__jdict1)
        obj2 = PersistentMessage.construct_from_jdict(self.__jdict1)
        self.assertEqual(True, obj1 == obj2)

    def test_neq(self):
        obj1 = PersistentMessage.construct_from_jdict(self.__jdict1)
        obj2 = PersistentMessage.construct_from_jdict(self.__jdict2)
        self.assertEqual(False, obj1 == obj2)

    def test_lt(self):
        obj1 = PersistentMessage.construct_from_jdict(self.__jdict2)
        obj2 = PersistentMessage.construct_from_jdict(self.__jdict1)
        self.assertEqual(True, obj1 < obj2)

    def test_nlt(self):
        obj1 = PersistentMessage.construct_from_jdict(self.__jdict1)
        obj2 = PersistentMessage.construct_from_jdict(self.__jdict2)
        self.assertEqual(False, obj1 < obj2)

    def test_as_db(self):
        obj1 = PersistentMessage.construct_from_jdict(self.__jdict1)
        self.assertEqual(('TST.001.002.MPU.001.100', '"hello"'), obj1.as_db_insert())

    def test_as_json(self):
        obj1 = PersistentMessage.construct_from_jdict(self.__jdict1)
        self.assertEqual('{"routing": "TST.001.002.MPU.001.100", "body": "hello"}', JSONify.dumps(obj1))


if __name__ == "__main_":
    unittest.main()
