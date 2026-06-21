"""
Created on 6 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

The state of a command station, as reported by a Z21 DCC command station

Classes in support of the Rocco Z21 DCC command station:
https://www.z21.eu/en/products/z21

Based on code:
https://github.com/botmonster/z21aio/tree/main
https://gitlab.com/z21-fpm/z21_python
"""

import struct

from mrcs_control.dcc.z21.command.dataset import Dataset
from mrcs_core.equipment.control_router.control_router_state import ControlRouterState


# --------------------------------------------------------------------------------------------------------------------

class Z21ControlRouterState(object):
    """
    The state of a command station, as reported by a Z21 DCC command station
    """


    @classmethod
    def construct_from_dataset(cls, dataset: Dataset) -> ControlRouterState:
        data = dataset.data

        if len(data) != 16:
            raise ValueError(f'Z21ControlRouterState data requires 16 bytes, got {data.hex(" ")}')

        (main_current, prog_current, filtered_main_current,
         temperature, supply_voltage, track_voltage, central_state,
         central_state_ext, reserved, capabilities) = struct.unpack('<hhhhHHBBBB', data)

        return ControlRouterState(main_current, prog_current, filtered_main_current,
                                  supply_voltage, track_voltage, temperature,
                                  central_state, central_state_ext, capabilities, reserved=reserved)
