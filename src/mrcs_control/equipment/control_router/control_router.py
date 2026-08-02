"""
Created on 31 Jul 2026

@author: Bruno Beloff (bbeloff@me.com)

An enumeration of all the cron node serial numbers
"""

from enum import IntEnum, unique

from mrcs_core.data.meta_enum import MetaEnum


# --------------------------------------------------------------------------------------------------------------------

@unique
class CRT(IntEnum, metaclass=MetaEnum):
    """
    An enumeration of all the cron nodes
    """

    Monitor = 1
    Commander = 2


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'{self.name}[{self.value}]'
