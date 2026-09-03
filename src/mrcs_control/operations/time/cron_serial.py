"""
Created on 25 Jan 2026

@author: Bruno Beloff (bbeloff@me.com)

An enumeration of all the cron node serial numbers
"""

from enum import IntEnum, unique

from mrcs_core.data.meta_enum import MetaEnum


# --------------------------------------------------------------------------------------------------------------------

@unique
class CronSerial(IntEnum, metaclass=MetaEnum):
    """
    An enumeration of all the cron nodes
    """

    CLOCK_MANAGER = 1
    CRON = 2
    CRONTAB = 3
    CLOCK_CONF = 4


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'{self.name}{{{self.value}}}'
