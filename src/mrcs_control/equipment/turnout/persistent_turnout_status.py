"""
Created on 4 Jul 2026

@author: Bruno Beloff (bbeloff@me.com)

SQLite database management for TurnoutStatus

{
    "type": "TurnoutStatus",
    "label": "TE01",
    "addr": 3,
    "position": "P1"
}
"""

from mrcs_control.data.persistence import PersistentObject
from mrcs_control.equipment.turnout.turnout_status_persistence import TurnoutStatusPersistence
from mrcs_core.equipment.turnout.turnout_enums import TurnoutPosition
from mrcs_core.equipment.turnout.turnout_status import TurnoutStatus


# --------------------------------------------------------------------------------------------------------------------

class PersistentTurnoutStatus(TurnoutStatus, TurnoutStatusPersistence, PersistentObject):
    """
    SQLite database management for TurnoutStatus
    """


    @classmethod
    def construct_from_db(cls, row, *child_rows) -> PersistentTurnoutStatus:
        label, block_label, turnout_address, position_name = row

        return cls(label, block_label, turnout_address, TurnoutPosition[position_name])


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, label: str, block_label: str, turnout_address: int, position: TurnoutPosition):
        super().__init__(label, block_label, turnout_address, position)


    # ----------------------------------------------------------------------------------------------------------------

    def save(self) -> None:
        type(self).insert(self)


    # ----------------------------------------------------------------------------------------------------------------

    def as_db_insert(self):
        return self.label, self.block_label, self.turnout_address, self.position.name


    def as_db_update(self):
        raise NotImplementedError('update is provided by TurnoutReport')
