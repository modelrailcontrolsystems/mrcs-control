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

from typing import List, Self

from mrcs_control.data.persistence import PersistentObject
from mrcs_control.equipment.block.block_status_persistence import BlockStatusPersistence
from mrcs_control.equipment.block.persistent_block_occupant import PersistentBlockOccupant
from mrcs_control.equipment.turnout.persistent_turnout_status import PersistentTurnoutStatus
from mrcs_core.equipment.block.block_enums import BlockDirection, BlockVoltage
from mrcs_core.equipment.block.block_occupant import BlockOccupant
from mrcs_core.equipment.block.block_status import BlockStatus
from mrcs_core.equipment.turnout.turnout_status import TurnoutStatus


# --------------------------------------------------------------------------------------------------------------------

class PersistentBlockStatus(BlockStatus, BlockStatusPersistence, PersistentObject):
    """
    a structured representation of a BlockStatus
    """


    @classmethod
    def construct_from_db(cls, row, *child_rows) -> Self:
        label, block_address, direction, voltage = row
        occupants = [PersistentBlockOccupant.construct_from_db(occupant_row) for occupant_row in child_rows]

        return cls(label, block_address, BlockDirection[direction], BlockVoltage[voltage], *occupants)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, label: str, block_address: str, direction: BlockDirection, voltage: BlockVoltage,
                 *occupants: BlockOccupant):
        super().__init__(label, block_address, direction, voltage, *occupants)


    # ----------------------------------------------------------------------------------------------------------------

    def save(self) -> None:
        type(self).insert(self)


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def turnouts(self) -> List[TurnoutStatus]:
        return PersistentTurnoutStatus.find_for_block(self.label)


    # ----------------------------------------------------------------------------------------------------------------

    def as_db_insert(self):
        return self.label, self.block_address, self.direction.name, self.voltage.name


    def as_db_update(self):
        raise NotImplementedError('use BlockReport classes instead')


    def children(self) -> List[PersistentBlockOccupant]:
        return [PersistentBlockOccupant.widen(occupant) for occupant in self.occupants]
