"""
Created on 14 Aug 2026

@author: Bruno Beloff (bbeloff@me.com)

a temporary inventory of turnouts
"""

import os.path
from typing import Any, List

from mrcs_core.data.json import PersistentJSONable
from mrcs_core.equipment.turnout.turnout_status import TurnoutStatus


# --------------------------------------------------------------------------------------------------------------------

class TurnoutInventory(PersistentJSONable):
    """
    a temporary inventory of turnouts
    """

    __FILENAME = "turnouts.json"


    @classmethod
    def persistence_location(cls):
        return os.path.join(cls.conf_dir(), 'inventory'), cls.__FILENAME


    @classmethod
    def construct_from_jdict(cls, jdict: Any):
        items = [TurnoutStatus.construct_from_jdict(item) for item in jdict]
        return cls(items)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, items: List[TurnoutStatus]):
        super().__init__()
        self.__items = items


    # ----------------------------------------------------------------------------------------------------------------

    def as_json(self, **kwargs):
        return self.items


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def items(self):
        return self.__items


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        items = '[' + ', '.join(str(item) for item in self.items) + ']'
        return f'TurnoutInventory:{{items:{items}}}'
