"""
Created on 10 Nov 2026

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v unit/operations/control_router/test_control_router_state.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import asyncio
import unittest
from unittest.mock import MagicMock

from mrcs_control.dcc.z21.command.station import Station
from mrcs_control.operations.control_router.control_router_state import ControlRouterState, Node
from mrcs_core.operations.state_machine import StateMachineException


# --------------------------------------------------------------------------------------------------------------------

class TestControlRouterState(unittest.TestCase):

    @staticmethod
    def __station() -> Station:
        # the state only stores the router, so a stand-in is sufficient
        return MagicMock(spec=Station)


    # ----------------------------------------------------------------------------------------------------------------

    def test_construct(self):
        obj1 = ControlRouterState()

        self.assertEqual(Node.STANDBY, obj1.node)
        self.assertTrue(obj1.is_STANDBY())
        self.assertFalse(obj1.is_READY())
        self.assertFalse(obj1.is_UNAVAILABLE())
        self.assertFalse(obj1.router_available_event.is_set())


    def test_router_not_ready(self):
        obj1 = ControlRouterState()

        with self.assertRaises(StateMachineException):
            _ = obj1.router


    def test_str(self):
        obj1 = ControlRouterState()
        self.assertEqual('ControlRouterState:{node:STANDBY, router:None}', str(obj1))


    # ----------------------------------------------------------------------------------------------------------------

    def test_go_READY(self):
        station = self.__station()

        obj1 = ControlRouterState()
        obj1.go_READY(station)

        self.assertTrue(obj1.is_READY())
        self.assertIs(station, obj1.router)
        self.assertTrue(obj1.router_available_event.is_set())


    def test_go_READY_from_READY(self):
        obj1 = ControlRouterState()
        obj1.go_READY(self.__station())

        with self.assertRaises(StateMachineException):
            obj1.go_READY(self.__station())


    # ----------------------------------------------------------------------------------------------------------------

    def test_go_UNAVAILABLE_from_READY(self):
        obj1 = ControlRouterState()
        obj1.go_READY(self.__station())
        obj1.go_UNAVAILABLE()

        self.assertTrue(obj1.is_UNAVAILABLE())
        self.assertFalse(obj1.router_available_event.is_set())
        self.assertEqual('ControlRouterState:{node:UNAVAILABLE, router:None}', str(obj1))

        with self.assertRaises(StateMachineException):
            _ = obj1.router


    def test_go_UNAVAILABLE_from_STANDBY(self):
        obj1 = ControlRouterState()
        obj1.go_UNAVAILABLE()
        self.assertTrue(obj1.is_UNAVAILABLE())


    def test_go_UNAVAILABLE_from_UNAVAILABLE(self):
        obj1 = ControlRouterState()
        obj1.go_UNAVAILABLE()

        with self.assertRaises(StateMachineException):
            obj1.go_UNAVAILABLE()

        self.assertTrue(obj1.is_UNAVAILABLE())


    def test_go_READY_from_UNAVAILABLE(self):
        obj1 = ControlRouterState()
        obj1.go_READY(self.__station())
        obj1.go_UNAVAILABLE()

        with self.assertRaises(StateMachineException):
            obj1.go_READY(self.__station())

        self.assertTrue(obj1.is_UNAVAILABLE())
        self.assertFalse(obj1.router_available_event.is_set())


    def test_go_READY_from_UNAVAILABLE_via_STANDBY(self):
        # as in ControlRouterNode.monitor(): a lost connection goes UNAVAILABLE, then STANDBY, then READY on retry
        station = self.__station()

        obj1 = ControlRouterState()
        obj1.go_READY(self.__station())
        obj1.go_UNAVAILABLE()
        obj1.go_STANDBY()
        obj1.go_READY(station)

        self.assertTrue(obj1.is_READY())
        self.assertIs(station, obj1.router)
        self.assertTrue(obj1.router_available_event.is_set())


    # ----------------------------------------------------------------------------------------------------------------

    def test_go_STANDBY_from_READY(self):
        obj1 = ControlRouterState()
        obj1.go_READY(self.__station())
        obj1.go_STANDBY()

        self.assertTrue(obj1.is_STANDBY())
        self.assertFalse(obj1.router_available_event.is_set())
        self.assertEqual('ControlRouterState:{node:STANDBY, router:None}', str(obj1))


    def test_go_STANDBY_from_UNAVAILABLE(self):
        obj1 = ControlRouterState()
        obj1.go_UNAVAILABLE()
        obj1.go_STANDBY()

        self.assertTrue(obj1.is_STANDBY())


    def test_go_STANDBY_from_STANDBY(self):
        # as in ControlRouterNode.monitor(), whose finally calls go_STANDBY() even if connect() failed
        obj1 = ControlRouterState()
        obj1.go_STANDBY()  # no exception - repeat calls are ignored

        self.assertTrue(obj1.is_STANDBY())
        self.assertFalse(obj1.router_available_event.is_set())


# --------------------------------------------------------------------------------------------------------------------

class TestControlRouterStateWait(unittest.IsolatedAsyncioTestCase):

    __TIMEOUT = 0.1  # seconds


    async def test_wait_when_ready(self):
        obj1 = ControlRouterState()
        obj1.go_READY(MagicMock(spec=Station))

        await asyncio.wait_for(obj1.wait_until_router_is_available(), self.__TIMEOUT)


    async def test_wait_until_ready(self):
        obj1 = ControlRouterState()
        waiter = asyncio.create_task(obj1.wait_until_router_is_available())

        await asyncio.sleep(0)
        self.assertFalse(waiter.done())

        obj1.go_READY(MagicMock(spec=Station))
        await asyncio.wait_for(waiter, self.__TIMEOUT)


    async def test_wait_when_unavailable(self):
        obj1 = ControlRouterState()
        obj1.go_READY(MagicMock(spec=Station))
        obj1.go_UNAVAILABLE()

        with self.assertRaises(asyncio.TimeoutError):
            await asyncio.wait_for(obj1.wait_until_router_is_available(), self.__TIMEOUT)


    async def test_wait_across_reconnect(self):
        # as in ControlRouterNode.monitor(): a waiter must survive READY -> UNAVAILABLE -> STANDBY -> READY
        obj1 = ControlRouterState()
        obj1.go_READY(MagicMock(spec=Station))
        obj1.go_UNAVAILABLE()

        waiter = asyncio.create_task(obj1.wait_until_router_is_available())
        await asyncio.sleep(0)

        obj1.go_STANDBY()
        await asyncio.sleep(0)
        self.assertFalse(waiter.done())

        obj1.go_READY(MagicMock(spec=Station))
        await asyncio.wait_for(waiter, self.__TIMEOUT)


# --------------------------------------------------------------------------------------------------------------------

class TestControlRouterStateLoops(unittest.TestCase):

    __TIMEOUT = 0.1  # seconds


    def test_wait_in_successive_loops(self):
        # as in successive ControlRouterNode.run() calls, each of which has its own event loop
        obj1 = ControlRouterState()

        async def wait_for_ready():
            waiter = asyncio.create_task(obj1.wait_until_router_is_available())
            await asyncio.sleep(0)

            obj1.go_READY(MagicMock(spec=Station))
            await asyncio.wait_for(waiter, self.__TIMEOUT)

            obj1.go_STANDBY()

        asyncio.run(wait_for_ready())
        asyncio.run(wait_for_ready())  # previously raised RuntimeError: ... bound to a different event loop


# --------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
