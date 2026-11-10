"""
Created on 10 Nov 2026

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v unit/operations/configuration_variable/test_cv_programmer_state.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import unittest

from mrcs_control.dcc.z21.command.command import XCommand
from mrcs_control.operations.configuration_variable.cv_programmer_state import CVProgrammerState, Node
from mrcs_core.inventory.configuration_variable.cv_address import CVAddress
from mrcs_core.inventory.configuration_variable.manufacturer_cv import ManufacturerCV
from mrcs_core.inventory.configuration_variable.numeric_cv import NumericCV
from mrcs_core.inventory.motive_power_unit.manufacturer import Manufacturer
from mrcs_core.operations.state_machine import StateMachineException


# --------------------------------------------------------------------------------------------------------------------

class TestCVProgrammerState(unittest.TestCase):

    def test_construct(self):
        obj1 = CVProgrammerState()

        self.assertEqual(Node.STANDBY, obj1.node)
        self.assertIsNone(obj1.decoder)
        self.assertEqual([], obj1.cv_queue)
        self.assertEqual([], obj1.cvs)


    def test_is_predicates(self):
        obj1 = CVProgrammerState()

        self.assertFalse(obj1.is_READ())
        self.assertFalse(obj1.is_WRITE())


    def test_str(self):
        obj1 = CVProgrammerState()
        self.assertEqual('CVProgrammerState:{node:STANDBY, decoder:None, cv_queue:[], cvs:[]}', str(obj1))


    # ----------------------------------------------------------------------------------------------------------------

    def test_go_READ(self):
        obj1 = CVProgrammerState()
        obj1.go_READ(CVAddress.ACCELERATION, CVAddress.DECELERATION)

        self.assertTrue(obj1.is_READ())
        self.assertEqual([CVAddress.ACCELERATION, CVAddress.DECELERATION], obj1.cv_queue)


    def test_go_READ_single(self):
        obj1 = CVProgrammerState()
        obj1.go_READ(CVAddress.ACCELERATION)
        self.assertEqual([CVAddress.ACCELERATION], obj1.cv_queue)


    def test_go_READ_all(self):
        # as used by CVProgrammer.read_all()
        obj1 = CVProgrammerState()
        obj1.go_READ(*CVAddress.items())
        self.assertEqual(list(CVAddress.items()), obj1.cv_queue)


    def test_go_READ_none(self):
        obj1 = CVProgrammerState()
        obj1.go_READ()
        self.assertEqual([], obj1.cv_queue)


    def test_go_READ_from_READ(self):
        obj1 = CVProgrammerState()
        obj1.go_READ(CVAddress.ACCELERATION)

        with self.assertRaises(StateMachineException):
            obj1.go_READ(CVAddress.DECELERATION)


    def test_go_WRITE_from_READ(self):
        obj1 = CVProgrammerState()
        obj1.go_READ(CVAddress.ACCELERATION)

        with self.assertRaises(StateMachineException):
            obj1.go_WRITE(None, NumericCV(CVAddress.ACCELERATION, 5))


    # ----------------------------------------------------------------------------------------------------------------

    def test_next_command_read(self):
        obj1 = CVProgrammerState()
        obj1.go_READ(CVAddress.ACCELERATION, CVAddress.DECELERATION)

        self.assertEqual(XCommand.lan_x_get_cv(CVAddress.ACCELERATION.value), obj1.next_command())
        self.assertEqual(XCommand.lan_x_get_cv(CVAddress.DECELERATION.value), obj1.next_command())
        self.assertEqual([], obj1.cv_queue)


    def test_next_command_read_exhausted(self):
        obj1 = CVProgrammerState()
        obj1.go_READ(CVAddress.ACCELERATION)
        obj1.next_command()

        with self.assertRaises(IndexError):
            obj1.next_command()


    def test_next_command_standby(self):
        obj1 = CVProgrammerState()

        with self.assertRaises(RuntimeError):
            obj1.next_command()


    # ----------------------------------------------------------------------------------------------------------------

    def test_go_WRITE(self):
        cvs = [NumericCV(CVAddress.ACCELERATION, 5), NumericCV(CVAddress.DECELERATION, 9)]

        obj1 = CVProgrammerState()
        obj1.go_WRITE(Manufacturer.ZIMO_ELEKTRONIK, *cvs)

        self.assertTrue(obj1.is_WRITE())
        self.assertEqual(Manufacturer.ZIMO_ELEKTRONIK, obj1.decoder)
        self.assertEqual(cvs, obj1.cv_queue)


    def test_next_command_write(self):
        obj1 = CVProgrammerState()
        obj1.go_WRITE(None, NumericCV(CVAddress.ACCELERATION, 5), NumericCV(CVAddress.DECELERATION, 9))

        self.assertEqual(XCommand.lan_x_set_cv(CVAddress.ACCELERATION.value, 5), obj1.next_command())
        self.assertEqual(XCommand.lan_x_set_cv(CVAddress.DECELERATION.value, 9), obj1.next_command())


    def test_next_command_write_skips_blacklisted(self):
        obj1 = CVProgrammerState()
        obj1.go_WRITE(None,
                      ManufacturerCV(CVAddress.MANUFACTURER_ID, Manufacturer.ZIMO_ELEKTRONIK),
                      NumericCV(CVAddress.MANUFACTURER_VERSION, 2),
                      NumericCV(CVAddress.ACCELERATION, 5))

        self.assertEqual(XCommand.lan_x_set_cv(CVAddress.ACCELERATION.value, 5), obj1.next_command())
        self.assertEqual([], obj1.cv_queue)


    def test_next_command_write_whitelisted_for_decoder(self):
        obj1 = CVProgrammerState()
        obj1.go_WRITE(Manufacturer.ZIMO_ELEKTRONIK, NumericCV(CVAddress.ZIMO_SPEED_CALIBRATION, 100))

        self.assertEqual(XCommand.lan_x_set_cv(CVAddress.ZIMO_SPEED_CALIBRATION.value, 100), obj1.next_command())


    def test_next_command_write_not_whitelisted_without_decoder(self):
        obj1 = CVProgrammerState()
        obj1.go_WRITE(None, NumericCV(CVAddress.ZIMO_SPEED_CALIBRATION, 100))

        with self.assertRaises(IndexError):
            obj1.next_command()


    def test_next_command_write_exhausted(self):
        obj1 = CVProgrammerState()
        obj1.go_WRITE(None)

        with self.assertRaises(IndexError):
            obj1.next_command()


    # ----------------------------------------------------------------------------------------------------------------

    def test_append_cv(self):
        cv1 = NumericCV(CVAddress.ACCELERATION, 5)
        cv2 = NumericCV(CVAddress.DECELERATION, 9)

        obj1 = CVProgrammerState()
        obj1.append_cv(cv1)
        obj1.append_cv(cv2)

        self.assertEqual([cv1, cv2], obj1.cvs)


# --------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
