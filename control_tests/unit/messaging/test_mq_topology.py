"""
Created on 5 Aug 2026

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v unit/messaging/test_mq_topology.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import unittest

from mrcs_control.messaging.mq_enums import MQMode, MQTopology
from mrcs_core.data.equipment_identity import EquipmentIdentifier, EquipmentType


# --------------------------------------------------------------------------------------------------------------------

class TestMQTopology(unittest.TestCase):

    def test_queue_single(self):
        obj1 = MQTopology.SINGLE
        obj2 = EquipmentIdentifier(EquipmentType.CRT, 1, 2)
        obj3 = obj1.value.queue_name(MQMode.TEST, obj2)
        self.assertEqual('MQMode.QueueConfiguration:{unique_name:False, durable:True, exclusive:False, '
                         'queue_name:mrcs.test.CRT.001.002}', str(obj1.value))
        self.assertEqual('mrcs.test.CRT.001.002', str(obj3))


    def test_queue_multiple(self):
        obj1 = MQTopology.MULTIPLE
        obj2 = EquipmentIdentifier(EquipmentType.CRT, 1, 2)
        obj3 = obj1.value.queue_name(MQMode.TEST, obj2)
        self.assertStartsWith(str(obj3), 'mrcs.test.CRT.001.002')
        self.assertTrue(len(str(obj3)) == 54)


# --------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
