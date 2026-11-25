"""
Created on 15 Nov 2026

@author: Bruno Beloff (bbeloff@me.com)

An enumeration of all the alert node serial numbers
"""

from enum import IntEnum, unique

from mrcs_core.data.meta_enum import MetaEnum


# --------------------------------------------------------------------------------------------------------------------

@unique
class AlertNodeSerial(IntEnum, metaclass=MetaEnum):
    """
    An enumeration of all the alert node serial numbers
    """

    NODE = 1  # listen for unprocessed alert messages
    UNRESOLVED = 2  # broadcast unresolved messages
    COMMAND = 3  # listen for / respond to commands


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'{self.name}{{{self.value}}}'
