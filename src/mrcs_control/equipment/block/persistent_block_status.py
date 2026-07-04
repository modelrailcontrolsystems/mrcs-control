"""
Created on 3 Jul 2026

@author: Bruno Beloff (bbeloff@me.com)

A structured representation of a BlockStatus

{
    "type": "BlockStatus",
    "label": "N01",
    "direction": "UP",
    "voltage": "OCCUPIED_WITH_VOLTAGE",
    "occupants": [
        {
            "addr": 4660,
            "face": "FWD"
        },
        {
            "addr": 17767,
            "face": "REV"
        }
    ]
}
"""

from mrcs_control.data.persistence import PersistentObject
from mrcs_control.equipment.block.block_status_persistence import BlockStatusPersistence
from mrcs_control.equipment.block.persistent_block_occupant import PersistentBlockOccupant

from mrcs_core.equipment.block.block_enums import BlockDirection, BlockVoltage
from mrcs_core.equipment.block.block_occupant import BlockOccupant
from mrcs_core.equipment.block.block_status import BlockStatus


# --------------------------------------------------------------------------------------------------------------------

class PersistentBlockStatus(BlockStatus, BlockStatusPersistence, PersistentObject):
    """
    a structured representation of a BlockStatus
    """


    @classmethod
    def construct_from_db(cls, row, occupant_rows):
        label, direction, voltage = row
        occupants = [PersistentBlockOccupant.construct_from_db(occupant_row) for occupant_row in occupant_rows]

        return cls(label, BlockDirection[direction], BlockVoltage[voltage], *occupants)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, label: str, direction: BlockDirection, voltage: BlockVoltage, *occupants: BlockOccupant):
        super().__init__(label, direction, voltage, *occupants)


    # ----------------------------------------------------------------------------------------------------------------

    def save(self):
        return super().insert(self)


    def save_block_only(self):
        return super().update(self)


    # ----------------------------------------------------------------------------------------------------------------

    def as_db_insert(self):
        return self.label, self.direction.name, self.voltage.name


    def as_db_update(self):
        return self.direction.name, self.voltage.name, self.label


    def children(self):
        return (PersistentBlockOccupant.widen(occupant) for occupant in self.occupants)
