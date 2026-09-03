"""
Created on 9 Aug 2026

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v unit/equipment/control_router/test_control_router_serial.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import unittest

from mrcs_control.operations.time.cron_serial import CronSerial


# --------------------------------------------------------------------------------------------------------------------

class TestCronSerial(unittest.TestCase):

    def test_cron_clock_manager(self):
        obj1 = CronSerial.CLOCK_MANAGER
        self.assertEqual('CLOCK_MANAGER{1}', str(obj1))


    def test_cron_cron(self):
        obj1 = CronSerial.CRON
        self.assertEqual('CRON{2}', str(obj1))


    def test_cron_crontab(self):
        obj1 = CronSerial.CRONTAB
        self.assertEqual('CRONTAB{3}', str(obj1))


    def test_cron_clock_conf(self):
        obj1 = CronSerial.CLOCK_CONF
        self.assertEqual('CLOCK_CONF{4}', str(obj1))
