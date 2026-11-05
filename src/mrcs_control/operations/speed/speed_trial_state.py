"""
Created on 31 Oct 2026

@author: Bruno Beloff (bbeloff@me.com)

The augmented states of a single speed trial journey
"""

from enum import StrEnum, unique

from mrcs_core.equipment.block.block_enums import BlockHeading
from mrcs_core.operations.speed.speed_log import SpeedLog
from mrcs_core.operations.speed.speed_trial_exception import SpeedTrialException
from mrcs_core.sys.logging import Logging


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

class SpeedTrialState(object):
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
    def is_permitted_transition(cls, a: Node, b: Node):
        return b in cls.__TRANSITIONS[a]


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, heading: BlockHeading = BlockHeading.UNASSIGNED, latest_reported_speed: int | None = None,
                 speed_log: SpeedLog | None = None):
        self.__node: Node = Node.STANDBY

        self.__heading = heading
        self.__latest_reported_speed = latest_reported_speed
        self.__speed_log = speed_log

        self.__logger = Logging.getLogger()


    # ----------------------------------------------------------------------------------------------------------------

    def is_STARTING(self):
        return self.node == Node.STARTING


    def is_TRIAL_RUNNING(self):
        return self.node == Node.TRIAL_RUNNING


    def is_TRIAL_ENDED(self):
        return self.node == Node.TRIAL_ENDED


    def is_STOPPING(self):
        return self.node == Node.STOPPING


    def is_STOPPED(self):
        return self.node == Node.STOPPED


    # ----------------------------------------------------------------------------------------------------------------

    def go_STARTING(self, heading: BlockHeading):
        self.__go(Node.STARTING)
        self.__heading = heading
        self.__latest_reported_speed = None
        self.__speed_log = None


    def go_TRIAL_RUNNING(self):
        self.__go(Node.TRIAL_RUNNING)
        self.__speed_log = SpeedLog.start(self.latest_reported_speed)


    def mark(self):
        if not self.node == Node.TRIAL_RUNNING:
            raise SpeedTrialException(f'Mark only permitted when TRIAL_RUNNING.')

        self.speed_log.mark(self.latest_reported_speed)


    def go_TRIAL_ENDED(self):
        self.__go(Node.TRIAL_ENDED)


    def go_STOPPING(self):
        self.__go(Node.STOPPING)
        self.speed_log.mark(self.latest_reported_speed)


    def go_STOPPED(self):
        self.__go(Node.STOPPED)


    # ----------------------------------------------------------------------------------------------------------------

    def __go(self, b: Node):
        if not self.is_permitted_transition(self.node, b):
            raise SpeedTrialException(f'No transition available from {self.node} to {b}.')

        self.node = b


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def node(self):
        return self.__node


    @node.setter
    def node(self, node: Node):
        self.logger.info(node)
        self.__node = node


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def heading(self):
        return self.__heading


    @property
    def latest_reported_speed(self) -> int:
        speed = self.__latest_reported_speed
        if speed is None:
            raise RuntimeError('Cannot report latest_reported_speed None.')

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


    @property
    def logger(self):
        return self.__logger


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'SpeedTrialState:{{node:{self.node}, heading:{self.heading.name}, '
                f'latest_reported_speed:{self.latest_reported_speed}, speed_log:{self.__speed_log}}}')
