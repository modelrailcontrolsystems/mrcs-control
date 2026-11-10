"""
Created on 31 Oct 2026

@author: Bruno Beloff (bbeloff@me.com)

The augmented states of a single speed trial journey
"""

from enum import StrEnum, unique

from mrcs_core.equipment.block.block_enums import BlockHeading
from mrcs_core.operations.speed.speed_log import SpeedLog
from mrcs_core.operations.state_machine import StateMachine


# --------------------------------------------------------------------------------------------------------------------

@unique
class Node(StrEnum):
    """
    the state machine nodes a single speed trial journey
    """

    STANDBY = 'STANDBY'
    STARTING = 'STARTING'
    TRIAL_RUNNING = 'TRIAL_RUNNING'
    TRIAL_ENDED = 'TRIAL_ENDED'
    STOPPING = 'STOPPING'
    STOPPED = 'STOPPED'


# --------------------------------------------------------------------------------------------------------------------

class SpeedTrialState(StateMachine[Node]):
    """
    the augmented states of a single speed trial journey
    """

    __TRANSITIONS = {
        Node.STANDBY: {Node.STARTING},
        Node.STARTING: {Node.TRIAL_RUNNING},
        Node.TRIAL_RUNNING: {Node.TRIAL_ENDED},
        Node.TRIAL_ENDED: {Node.STOPPING},
        Node.STOPPING: {Node.STOPPED},
        Node.STOPPED: {Node.STANDBY, Node.STARTING}
    }


    @classmethod
    def transitions(cls) -> dict[Node, set[Node]]:
        return cls.__TRANSITIONS


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, heading: BlockHeading = BlockHeading.UNASSIGNED, latest_reported_speed: int | None = None,
                 speed_log: SpeedLog | None = None):
        super().__init__(Node.STANDBY)

        self.__heading = heading
        self.__latest_reported_speed = latest_reported_speed
        self.__speed_log = speed_log


    # ----------------------------------------------------------------------------------------------------------------

    def is_STARTING(self) -> bool:
        return self._is(Node.STARTING)


    def is_TRIAL_RUNNING(self) -> bool:
        return self._is(Node.TRIAL_RUNNING)


    def is_TRIAL_ENDED(self) -> bool:
        return self._is(Node.TRIAL_ENDED)


    def is_STOPPING(self) -> bool:
        return self._is(Node.STOPPING)


    def is_STOPPED(self) -> bool:
        return self._is(Node.STOPPED)


    # ----------------------------------------------------------------------------------------------------------------

    def go_STARTING(self, heading: BlockHeading) -> None:
        self._go(Node.STARTING)
        self.__heading = heading
        self.__latest_reported_speed = None
        self.__speed_log = None


    def go_TRIAL_RUNNING(self) -> None:
        latest_reported_speed = self.latest_reported_speed  # check there is a speed

        self._go(Node.TRIAL_RUNNING)
        self.__speed_log = SpeedLog.start(latest_reported_speed)


    def mark(self) -> None:
        if not self._is(Node.TRIAL_RUNNING):
            raise RuntimeError(f'Mark only permitted when TRIAL_RUNNING.')

        self.speed_log.mark(self.latest_reported_speed)


    def go_TRIAL_ENDED(self) -> None:
        self._go(Node.TRIAL_ENDED)


    def go_STOPPING(self) -> None:
        self._go(Node.STOPPING)
        self.speed_log.mark(self.latest_reported_speed)


    def go_STOPPED(self) -> None:
        self._go(Node.STOPPED)


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def heading(self):
        return self.__heading


    @property
    def latest_reported_speed(self) -> int:
        speed = self.__latest_reported_speed
        if speed is None:
            raise RuntimeError('There is no latest reported speed.')

        return speed


    @latest_reported_speed.setter
    def latest_reported_speed(self, latest_reported_speed: int):
        self.__latest_reported_speed = latest_reported_speed


    @property
    def speed_log(self) -> SpeedLog:
        speed_log = self.__speed_log
        if speed_log is None:
            raise RuntimeError('Cannot report speed_log None.')

        return speed_log


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'SpeedTrialState:{{node:{self.node}, heading:{self.heading.name}, '
                f'latest_reported_speed:{self.__latest_reported_speed}, speed_log:{self.__speed_log}}}')
