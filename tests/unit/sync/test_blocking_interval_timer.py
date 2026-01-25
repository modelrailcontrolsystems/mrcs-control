"""
Created on 15 Nov 2025

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v messaging/test_message.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""
import time
import unittest

from mrcs_control.sys.interval_timer import BlockingIntervalTimer


# --------------------------------------------------------------------------------------------------------------------

class TestBlockingIntervalTimer(unittest.TestCase):
    def test_construct(self):
        obj1 = BlockingIntervalTimer(1.5)
        self.assertEqual('BlockingIntervalTimer:{interval:1.500, time_to_next_yield:1.500}', str(obj1))

    def test_true(self):
        start = time.time()
        obj1 = BlockingIntervalTimer(1.5)
        response = obj1.true()
        end = time.time()
        period = round(end - start, 1)

        self.assertTrue(response)
        self.assertEqual(1.5, period)

    def test_interval(self):
        start = time.time()
        obj1 = BlockingIntervalTimer(1.5)
        obj1.interval = 2.0
        response = obj1.true()
        end = time.time()
        period = round(end - start, 1)

        self.assertTrue(response)
        self.assertEqual(2.0, period)


if __name__ == "__main_":
    unittest.main()
