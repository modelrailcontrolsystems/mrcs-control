"""
Created on 9 Nov 2026

@author: Bruno Beloff (bbeloff@me.com)

The augmented states of a CV programing task
"""

from enum import StrEnum, unique

from mrcs_control.dcc.z21.command.command import Command, XCommand
from mrcs_core.inventory.configuration_variable.cv import CV
from mrcs_core.inventory.configuration_variable.cv_address import CVAddress
from mrcs_core.inventory.motive_power_unit.manufacturer import Manufacturer
from mrcs_core.operations.state_machine import StateMachine


# --------------------------------------------------------------------------------------------------------------------

@unique
class Node(StrEnum):
    """
    the state machine nodes a CV programing task
    """

    STANDBY = 'STANDBY'
    READ = 'READ'
    WRITE = 'WRITE'


# --------------------------------------------------------------------------------------------------------------------

class CVProgrammerState(StateMachine[Node]):
    """
    the augmented states of a CV programing task
    """

    __TRANSITIONS = {
        Node.STANDBY: {Node.READ, Node.WRITE},
        Node.READ: {Node.STANDBY},
        Node.WRITE: {Node.STANDBY},
    }


    @classmethod
    def transitions(cls) -> dict[Node, set[Node]]:
        return cls.__TRANSITIONS


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self):
        super().__init__(Node.STANDBY)

        self.__decoder = None
        self.__cv_queue = []
        self.__cvs = []


    # ----------------------------------------------------------------------------------------------------------------

    def is_READ(self) -> bool:
        return self._is(Node.READ)


    def is_WRITE(self) -> bool:
        return self._is(Node.WRITE)


    # ----------------------------------------------------------------------------------------------------------------

    def go_READ(self, *cv_addresses: CVAddress) -> None:
        self._go(Node.READ)
        self.__cv_queue = list(cv_addresses)


    def go_WRITE(self, decoder: Manufacturer | None, *cvs: CV) -> None:
        self._go(Node.WRITE)
        self.__cv_queue = list(cvs)
        self.__decoder = decoder


    # ----------------------------------------------------------------------------------------------------------------

    def next_command(self) -> Command:
        if self.is_READ():
            return self.__next_read_command()

        if self.is_WRITE():
            return self.__next_write_command()

        raise RuntimeError(f'No next command when in state {self.node}.')


    def __next_read_command(self) -> Command:
        cv_address = self.cv_queue.pop(0)  # may raise IndexError

        return XCommand.lan_x_get_cv(cv_address.value)


    def __next_write_command(self) -> Command:
        while True:
            cv = self.cv_queue.pop(0)  # may raise IndexError
            if cv.is_writeable(self.decoder):
                break

        return XCommand.lan_x_set_cv(cv.cv_address.value, cv.value)


    def append_cv(self, cv: CV) -> None:
        self.logger.info(cv)
        self.cvs.append(cv)


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def decoder(self):
        return self.__decoder


    @property
    def cv_queue(self):
        return self.__cv_queue


    @property
    def cvs(self):
        return self.__cvs


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'CVProgrammerState:{{node:{self.node}, decoder:{self.decoder}, '
                f'cv_queue:{self.cv_queue}, cvs:{self.cvs}}}')
