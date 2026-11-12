"""
Created on 9 Nov 2026

@author: Bruno Beloff (bbeloff@me.com)

The augmented states of a control router connection
"""

import asyncio
from enum import StrEnum, unique

from mrcs_control.dcc.z21.command.station import Station
from mrcs_core.operations.state_machine import StateMachine, StateMachineException


# --------------------------------------------------------------------------------------------------------------------

@unique
class Node(StrEnum):
    """
    the state machine nodes a control router connection
    """

    STANDBY = 'STANDBY'
    READY = 'READY'
    UNAVAILABLE = 'UNAVAILABLE'


# --------------------------------------------------------------------------------------------------------------------

class ControlRouterState(StateMachine[Node]):
    """
    the augmented states of a control router connection
    """

    __TRANSITIONS = {
        Node.STANDBY: {Node.READY, Node.UNAVAILABLE},
        Node.READY: {Node.UNAVAILABLE, Node.STANDBY},
        Node.UNAVAILABLE: {Node.STANDBY},
    }


    @classmethod
    def transitions(cls) -> dict[Node, set[Node]]:
        return cls.__TRANSITIONS


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self):
        super().__init__(Node.STANDBY)

        self.__router = None

        self.__router_available_event: asyncio.Event | None = None
        self.__event_loop: asyncio.AbstractEventLoop | None = None


    # ----------------------------------------------------------------------------------------------------------------

    def is_STANDBY(self) -> bool:
        return self._is(Node.STANDBY)


    def is_READY(self) -> bool:
        return self._is(Node.READY)


    def is_UNAVAILABLE(self) -> bool:
        return self._is(Node.UNAVAILABLE)


    # ----------------------------------------------------------------------------------------------------------------

    def go_STANDBY(self) -> None:
        if self.is_STANDBY():
            return

        self._go(Node.STANDBY)
        self.__router = None
        self.router_available_event.clear()


    def go_READY(self, router: Station) -> None:
        self._go(Node.READY)
        self.__router = router
        self.router_available_event.set()


    def go_UNAVAILABLE(self) -> None:
        self._go(Node.UNAVAILABLE)
        self.__router = None
        self.router_available_event.clear()


    # ----------------------------------------------------------------------------------------------------------------

    async def wait_until_router_is_available(self):
        await self.router_available_event.wait()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def router(self):
        if not self.is_READY():
            raise StateMachineException('The router is not ready.')

        return self.__router


    @property
    def router_available_event(self) -> asyncio.Event:
        # an asyncio.Event is bound to the event loop that first waits on it, so each loop needs its own event -
        # within a loop, the same event is kept, so that waiters survive STANDBY -> READY cycles
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        event = self.__router_available_event

        if event is None or loop is not self.__event_loop:
            event = asyncio.Event()

            if self.is_READY():
                event.set()

            self.__router_available_event = event
            self.__event_loop = loop

        return event


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'ControlRouterState:{{node:{self.node}, router:{self.__router}}}'
