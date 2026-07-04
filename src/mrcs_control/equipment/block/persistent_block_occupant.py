"""
Created on 3 Jul 2026

@author: Bruno Beloff (bbeloff@me.com)

A structured representation of a BlockOccupant

{
    "addr": 17767,
    "face": "REV"
}
"""

from mrcs_control.data.persistence import PersistentObject
from mrcs_control.equipment.block.block_status_persistence import BlockStatusPersistence

from mrcs_core.equipment.block.block_enums import BlockOccupantFace
from mrcs_core.equipment.block.block_occupant import BlockOccupant


# --------------------------------------------------------------------------------------------------------------------

class PersistentBlockOccupant(BlockOccupant, BlockStatusPersistence, PersistentObject):
    """
    A structured representation of a BlockOccupant
    """


    @classmethod
    def widen(cls, occupant: BlockOccupant):
        return cls(occupant.address, occupant.face)


    @classmethod
    def construct_from_db(cls, row):
        address, face = row

        return cls(int(address), BlockOccupantFace[face])


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, address: int, face: BlockOccupantFace):
        super().__init__(address, face)


    # ----------------------------------------------------------------------------------------------------------------

    def save(self):
        raise NotImplementedError('use BlockStatus class instead')


    # ----------------------------------------------------------------------------------------------------------------

    def as_db_insert(self):
        return self.address, self.face.name


    def as_db_update(self):
        raise NotImplementedError('only INSERT is supported')
