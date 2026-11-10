"""
Created on 10 Nov 2026

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v unit/operations/speed/test_speed_trial_state.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import unittest

from mrcs_control.operations.speed.speed_trial_state import Node, SpeedTrialState
from mrcs_core.equipment.block.block_enums import BlockHeading
from mrcs_core.operations.state_machine import StateMachineException


# --------------------------------------------------------------------------------------------------------------------

class TestSpeedTrialState(unittest.TestCase):

    @staticmethod
    def __running_state(speed: int) -> SpeedTrialState:
        state = SpeedTrialState()
        state.go_STARTING(BlockHeading.UP)
        state.latest_reported_speed = speed
        state.go_TRIAL_RUNNING()

        return state


    @classmethod
    def __stopped_state(cls) -> SpeedTrialState:
        state = cls.__running_state(20)
        state.go_TRIAL_ENDED()
        state.go_STOPPING()
        state.go_STOPPED()

        return state


    # ----------------------------------------------------------------------------------------------------------------

    def test_construct(self):
        obj1 = SpeedTrialState()
        self.assertEqual(Node.STANDBY, obj1.node)
        self.assertEqual(BlockHeading.UNASSIGNED, obj1.heading)


    def test_construct_with_speed(self):
        obj1 = SpeedTrialState(BlockHeading.DOWN, 12)
        self.assertEqual(BlockHeading.DOWN, obj1.heading)
        self.assertEqual(12, obj1.latest_reported_speed)


    def test_latest_reported_speed_none(self):
        obj1 = SpeedTrialState()
        with self.assertRaises(RuntimeError):
            _ = obj1.latest_reported_speed


    def test_latest_reported_speed_set(self):
        obj1 = SpeedTrialState()
        obj1.latest_reported_speed = 30
        self.assertEqual(30, obj1.latest_reported_speed)


    def test_speed_log_none(self):
        obj1 = SpeedTrialState()
        with self.assertRaises(RuntimeError):
            _ = obj1.speed_log


    # ----------------------------------------------------------------------------------------------------------------

    def test_transitions(self):
        self.assertEqual(set(Node), set(SpeedTrialState.transitions().keys()))


    def test_is_predicates(self):
        obj1 = SpeedTrialState()
        predicates = [obj1.is_STARTING, obj1.is_TRIAL_RUNNING, obj1.is_TRIAL_ENDED, obj1.is_STOPPING,
                      obj1.is_STOPPED]

        self.assertEqual([False] * 5, [predicate() for predicate in predicates])


    # ----------------------------------------------------------------------------------------------------------------

    def test_go_STARTING(self):
        obj1 = SpeedTrialState()
        obj1.go_STARTING(BlockHeading.DOWN)

        self.assertTrue(obj1.is_STARTING())
        self.assertEqual(BlockHeading.DOWN, obj1.heading)


    def test_go_STARTING_resets_speed(self):
        obj1 = SpeedTrialState(latest_reported_speed=12)
        obj1.go_STARTING(BlockHeading.UP)

        with self.assertRaises(RuntimeError):
            _ = obj1.latest_reported_speed


    def test_go_TRIAL_RUNNING(self):
        obj1 = self.__running_state(20)

        self.assertTrue(obj1.is_TRIAL_RUNNING())
        self.assertEqual(1, len(obj1.speed_log))
        self.assertEqual(20, obj1.speed_log.reports[0].reported_speed)


    def test_mark(self):
        obj1 = self.__running_state(20)
        obj1.latest_reported_speed = 25
        obj1.mark()

        self.assertEqual([20, 25], [report.reported_speed for report in obj1.speed_log.reports])


    def test_mark_not_running(self):
        obj1 = SpeedTrialState()
        with self.assertRaises(RuntimeError):
            obj1.mark()


    def test_go_TRIAL_ENDED(self):
        obj1 = self.__running_state(20)
        obj1.go_TRIAL_ENDED()
        self.assertTrue(obj1.is_TRIAL_ENDED())


    def test_mark_after_trial_ended(self):
        obj1 = self.__running_state(20)
        obj1.go_TRIAL_ENDED()

        with self.assertRaises(RuntimeError):
            obj1.mark()


    def test_go_STOPPING(self):
        obj1 = self.__running_state(20)
        obj1.go_TRIAL_ENDED()
        obj1.latest_reported_speed = 18
        obj1.go_STOPPING()

        self.assertTrue(obj1.is_STOPPING())
        self.assertEqual([20, 18], [report.reported_speed for report in obj1.speed_log.reports])


    def test_go_STOPPED(self):
        obj1 = self.__stopped_state()
        self.assertTrue(obj1.is_STOPPED())


    def test_full_journey_speed_log(self):
        obj1 = self.__stopped_state()
        self.assertEqual(2, len(obj1.speed_log))


    # ----------------------------------------------------------------------------------------------------------------

    def test_restart_after_stopped(self):
        obj1 = self.__stopped_state()
        obj1.go_STARTING(BlockHeading.DOWN)

        self.assertTrue(obj1.is_STARTING())
        self.assertEqual(BlockHeading.DOWN, obj1.heading)

        with self.assertRaises(RuntimeError):
            _ = obj1.speed_log


    def test_go_TRIAL_RUNNING_from_STANDBY(self):
        obj1 = SpeedTrialState()
        obj1.latest_reported_speed = 20

        with self.assertRaises(StateMachineException):
            obj1.go_TRIAL_RUNNING()


    def test_go_TRIAL_RUNNING_no_speed(self):
        obj1 = SpeedTrialState()
        obj1.go_STARTING(BlockHeading.UP)

        with self.assertRaises(RuntimeError):
            obj1.go_TRIAL_RUNNING()

        self.assertTrue(obj1.is_STARTING())


    def test_go_STOPPING_from_TRIAL_RUNNING(self):
        obj1 = self.__running_state(20)

        with self.assertRaises(StateMachineException):
            obj1.go_STOPPING()

        self.assertTrue(obj1.is_TRIAL_RUNNING())


    def test_go_STARTING_from_TRIAL_RUNNING(self):
        obj1 = self.__running_state(20)

        with self.assertRaises(StateMachineException):
            obj1.go_STARTING(BlockHeading.DOWN)

        self.assertEqual(BlockHeading.UP, obj1.heading)


    # ----------------------------------------------------------------------------------------------------------------

    def test_str(self):
        obj1 = SpeedTrialState(BlockHeading.UP, 20)
        self.assertEqual('SpeedTrialState:{node:STANDBY, heading:UP, latest_reported_speed:20, speed_log:None}',
                         str(obj1))


    def test_str_new(self):
        obj1 = SpeedTrialState()
        self.assertEqual('SpeedTrialState:{node:STANDBY, heading:UNASSIGNED, latest_reported_speed:None, '
                         'speed_log:None}', str(obj1))


# --------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
