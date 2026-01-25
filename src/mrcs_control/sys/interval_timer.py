"""
Created on 11 Jul 2016

@author: Bruno Beloff (bbeloff@me.com)

Provides equally-spaced intervals. Available in both blocking and async flavours.
"""

import asyncio
import time

from abc import ABC


# --------------------------------------------------------------------------------------------------------------------

class IntervalTimer(ABC):
    """
    generate yields at pre-set intervals
    """

    def __init__(self, interval: float):
        self.__interval = interval
        self._next_yield = time.time() + self.__interval


    # ----------------------------------------------------------------------------------------------------------------

    def reset(self):
        self._next_yield = time.time() + self.__interval


    def _sleep_time(self):
        sleep_time = self.time_to_next_yield % self.interval

        if sleep_time == 0:
            sleep_time = self.interval

        return sleep_time


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def interval(self):
        return self.__interval


    @interval.setter
    def interval(self, interval):
        self.__interval = interval
        self.reset()


    @property
    def next_yield(self):
        return self._next_yield


    @property
    def time_to_next_yield(self):
        return abs(self.next_yield - time.time())           # time to next must always be positive


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'{self.__class__.__name__}:{{interval:{self.interval:.3f}, '
                f'time_to_next_yield:{self.time_to_next_yield:.3f}}}')


# --------------------------------------------------------------------------------------------------------------------

class BlockingIntervalTimer(IntervalTimer):
    """
    generate yields at pre-set intervals (blocking)
    """

    def __init__(self, interval: float):
        super().__init__(interval)


    # ----------------------------------------------------------------------------------------------------------------

    def true(self) -> bool:
        try:
            self.__sleep_until_next_yield()
        except KeyboardInterrupt:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    def __sleep_until_next_yield(self):
        if self.interval == 0:
            return

        time.sleep(self._sleep_time())
        self._next_yield += self.interval


# --------------------------------------------------------------------------------------------------------------------

class AsyncIntervalTimer(IntervalTimer):
    """
    generate yields at pre-set intervals (async)
    """

    def __init__(self, interval: float):
        super().__init__(interval)


    # ----------------------------------------------------------------------------------------------------------------

    async def next(self):
        try:
            await self.__sleep_until_next_yield()
        except KeyboardInterrupt:
            pass


    # ----------------------------------------------------------------------------------------------------------------

    async def __sleep_until_next_yield(self):
        if self.interval == 0:
            return

        await asyncio.sleep(self._sleep_time())
        self._next_yield += self.interval

