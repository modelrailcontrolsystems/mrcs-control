"""
Created on 25 Jan 2026

@author: Bruno Beloff (bbeloff@me.com)

An enumeration of all the cron node serial numbers
"""

from enum import IntEnum, unique

from mrcs_core.data.meta_enum import MetaEnum


# --------------------------------------------------------------------------------------------------------------------

@unique
class CRN(IntEnum, metaclass=MetaEnum):
    """
    An enumeration of all the cron nodes
    """

    ClockManager = 1
    Cron = 2
    Crontab = 3
    ClockConf = 4


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'{self.name}[{self.value}]'
