"""
Created on 15 Nov 2026

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v unit/operations/alert/test_resolution_command.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import json
import unittest

from mrcs_control.operations.alert.resolution_response import ResolutionResponse
from mrcs_core.data.json import JSONify


# --------------------------------------------------------------------------------------------------------------------

class TestResolutionResponse(unittest.TestCase):

    def test_construct(self):
        obj1 = ResolutionResponse(1, error=str(RuntimeError('something went wrong')))
        self.assertEqual('ResolutionResponse:{alert_id:1, error:something went wrong}', str(obj1))


    def test_json(self):
        obj1 = ResolutionResponse(1, error=str(RuntimeError('something went wrong')))
        jstr = JSONify.dumps(obj1)
        self.assertEqual('{"type": "ResolutionResponse", "alert_id": 1, "error": "something went wrong"}', jstr)


    def test_json_eq(self):
        obj1 = ResolutionResponse(1, error=str(RuntimeError('something went wrong')))
        jstr = JSONify.dumps(obj1)
        obj2 = ResolutionResponse.construct_from_jdict(json.loads(jstr))
        self.assertTrue(obj1 == obj2)


    def test_neq(self):
        obj1 = ResolutionResponse(1, error=str(RuntimeError('something went wrong')))
        obj2 = ResolutionResponse(1)
        self.assertFalse(obj1 == obj2)


    def test_ACK(self):
        obj1 = ResolutionResponse(1)
        self.assertTrue(obj1.is_ACK())


    def test_NACK(self):
        obj1 = ResolutionResponse(1, error=str(RuntimeError('something went wrong')))
        self.assertTrue(obj1.is_NACK())


# --------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
