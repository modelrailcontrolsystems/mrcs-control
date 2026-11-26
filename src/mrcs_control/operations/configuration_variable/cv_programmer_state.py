"""
Created on 9 Nov 2026

@author: Bruno Beloff (bbeloff@me.com)

The augmented states of a CV programmer
"""

from enum import StrEnum, unique
from typing import cast

from mrcs_control.dcc.z21.command.command import Command, XCommand
from mrcs_core.inventory.configuration_variable import CVMetadata
from mrcs_core.inventory.configuration_variable.cv_address import CVAddress
from mrcs_core.inventory.configuration_variable.types.cv import CV
from mrcs_core.inventory.configuration_variable.types.manufacturer_cv import ManufacturerCV
from mrcs_core.inventory.manufacturer.manufacturer import Manufacturer
from mrcs_core.operations.state_machine import StateMachine


# --------------------------------------------------------------------------------------------------------------------

@unique
class Node(StrEnum):
    """
    the nodes a CV programmer state machine
    """

    STANDBY = 'STANDBY'
    READ = 'READ'
    WRITE = 'WRITE'


# --------------------------------------------------------------------------------------------------------------------

class CVProgrammerState(StateMachine[Node]):
    """
    the augmented states of a CV programmer
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

        self.__decoder: Manufacturer | None = None
        self.__cv_queue = []
        self.__cvs: list[CV] = []


    # ----------------------------------------------------------------------------------------------------------------

    def is_READ(self) -> bool:
        return self._is(Node.READ)


    def is_WRITE(self) -> bool:
        return self._is(Node.WRITE)


    # ----------------------------------------------------------------------------------------------------------------

    def go_READ(self, *addresses: CVAddress) -> None:
        self._go(Node.READ)
        self.__cv_queue = list(addresses)


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
        while True:
            address = self.cv_queue.pop(0)  # may raise IndexError
            cv_meta = CVMetadata.find(address)
            if cv_meta.may_be_read_from(self.decoder):
                break

        return XCommand.lan_x_get_cv(address.value)


    def __next_write_command(self) -> Command:
        while True:
            cv = self.cv_queue.pop(0)  # may raise IndexError
            if cv.may_be_written_to(self.decoder):
                break
            else:
                self.logger.warn(f'the CV {cv} was present, but must not be written')

        return XCommand.lan_x_set_cv(cv.address.value, cv.value)


    def append_cv(self, cv: CV) -> None:
        self.logger.info(cv)
        self.cvs.append(cv)

        if cv.address == CVAddress.MANUFACTURER_ID:
            self.__decoder = cast(ManufacturerCV, cv).manufacturer


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
