"""
Created on 5 Aug 2026

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v unit/operations/test_node_topology.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import json
import unittest
from pathlib import Path

from mrcs_control.operations.node_enums import NodeTopology
from mrcs_core.messaging.exchange import Exchange


# --------------------------------------------------------------------------------------------------------------------

class TestNodeTopology(unittest.TestCase):
    __filename1 = Path(__file__).parent / 'data' / 'exchange.json'
    with open(__filename1) as fp:
        __jdict1 = json.load(fp)


    def test_node_test(self):
        obj1 = NodeTopology.TEST
        self.assertEqual('NodeTopology.ServiceConfiguration:{id:TEST, db_mode:test, mq_mode:mrcs.test}',
                         str(obj1.value))


    def test_node_live(self):
        obj1 = NodeTopology.LIVE
        self.assertEqual('NodeTopology.ServiceConfiguration:{id:LIVE, db_mode:live, mq_mode:mrcs.live}',
                         str(obj1.value))


    def test_broker_filter(self):
        obj1 = NodeTopology.TEST
        obj2 = Exchange.construct_from_jdict(self.__jdict1)
        obj3 = obj1.value.broker_filter([obj2])
        self.assertEqual('Exchange:{name:mrcs.test, exchange_type:topic, durable:True, internal:False, '
                         'auto_delete:False, message_stats:MessageStats:{publish_in:14637, publish_out:14604}}',
                         str(obj3[0]))


# --------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
