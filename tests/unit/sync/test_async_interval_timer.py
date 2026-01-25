"""
Created on 15 Nov 2025

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v messaging/test_message.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import time
import unittest

from mrcs_control.sys.interval_timer import AsyncIntervalTimer


# --------------------------------------------------------------------------------------------------------------------

class TestAsyncIntervalTimer(unittest.TestCase):
    def test_construct(self):
        obj1 = AsyncIntervalTimer(1.5)
        self.assertEqual('AsyncIntervalTimer:{interval:1.500, time_to_next_yield:1.500}', str(obj1))

    async def test_next(self):
        start = time.time()
        obj1 = AsyncIntervalTimer(1.5)
        await obj1.next()
        end = time.time()
        period = round(end - start, 1)

        self.assertEqual(1.5, period)

    async def test_interval(self):
        start = time.time()
        obj1 = AsyncIntervalTimer(1.5)
        obj1.interval = 2.0
        await obj1.next()
        end = time.time()
        period = round(end - start, 1)

        self.assertEqual(2.0, period)


if __name__ == "__main_":
    unittest.main()
