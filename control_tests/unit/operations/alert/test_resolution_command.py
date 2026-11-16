"""
Created on 15 Nov 2026

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v unit/operations/alert/test_resolution_command.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import json
import unittest

from mrcs_control.operations.alert.resolution_command import ResolutionCommand
from mrcs_core.data.json import JSONify


# --------------------------------------------------------------------------------------------------------------------

class TestResolutionCommand(unittest.TestCase):

    def test_construct(self):
        obj1 = ResolutionCommand(1, True)
        self.assertEqual('ResolutionCommand:{alert_id:1, requires_response:True}', str(obj1))


    def test_json(self):
        obj1 = ResolutionCommand(1, True)
        jstr = JSONify.dumps(obj1)
        self.assertEqual('{"type": "ResolutionCommand", "alert_id": 1, "requires_response": true}', jstr)


    def test_json_eq(self):
        obj1 = ResolutionCommand(1, True)
        jstr = JSONify.dumps(obj1)
        obj2 = ResolutionCommand.construct_from_jdict(json.loads(jstr))
        self.assertTrue(obj1 == obj2)


    def test_neq(self):
        obj1 = ResolutionCommand(1, True)
        obj2 = ResolutionCommand(1, False)
        self.assertFalse(obj1 == obj2)


# --------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
