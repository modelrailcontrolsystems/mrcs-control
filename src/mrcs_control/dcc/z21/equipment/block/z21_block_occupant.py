"""
Created on 16 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

An MPU occupant of a block, as reported by a Z21 DCC command station

Based on the Roco 10808 detector:
https://www.roco.cc/ren/products/control/accessories/10808-z21-detector.html

Classes in support of the Rocco Z21 DCC command station:
https://www.z21.eu/en/products/z21

Based on code:
https://github.com/botmonster/z21aio/tree/main
https://gitlab.com/z21-fpm/z21_python
"""

from mrcs_core.equipment.block.block_occupant import BlockOccupant
from mrcs_core.equipment.block.block_occupant_face import BlockOccupantFace


# --------------------------------------------------------------------------------------------------------------------

class Z21BlockOccupant(object):
    """
    An MPU occupant of a block, as reported by a Z21 DCC command station
    """


    @classmethod
    def construct_from_data(cls, data: int) -> BlockOccupant:
        address = data & 0x3fff

        # may raise ValueError
        face = BlockOccupantFace((data >> 14) & 0x0003)

        return BlockOccupant(address, face)
