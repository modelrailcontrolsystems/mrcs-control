"""
Created on 14 Aug 2026

@author: Bruno Beloff (bbeloff@me.com)

a temporary inventory of turnouts
"""

from typing import Any, List, Self

from mrcs_core.data.json import PersistentJSONable
from mrcs_core.equipment.block.block_status import BlockStatus


# --------------------------------------------------------------------------------------------------------------------

class BlockInventory(PersistentJSONable):
    """
    a temporary inventory of turnouts
    """

    __FILENAME = "blocks.json"


    @classmethod
    def persistence_location(cls):
        return cls.inventory_dir(), cls.__FILENAME


    @classmethod
    def construct_from_jdict(cls, jdict: Any) -> Self:
        items = [BlockStatus.construct_from_jdict(item) for item in jdict]
        return cls(items)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, items: List[BlockStatus]):
        super().__init__()
        self.__items = items


    def __len__(self):
        return len(self.__items)


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
        return f'BlockInventory:{{items:{items}}}'
