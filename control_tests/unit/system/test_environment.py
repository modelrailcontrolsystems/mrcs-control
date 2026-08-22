"""
Created on 17 Aug 2026

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v unit/system/test_environment.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import unittest

from mrcs_control.operations.node_topology import NodeTopology
from mrcs_control.sys.environment import Environment
from mrcs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

class TestEnvironment(unittest.IsolatedAsyncioTestCase):

    def test_get(self):
        Logging.config('test', verbose=True)
        obj1 = Environment.get()
        self.assertEqual('Environment:{log_name:, log_level:20, queuing:NodeTopology.TEST}', str(obj1))


    def test_set(self):
        Logging.config('test', verbose=True)
        Environment.set(NodeTopology.LIVE)
        obj1 = Environment.get()
        self.assertEqual('Environment:{log_name:test, log_level:20, queuing:NodeTopology.LIVE}', str(obj1))
