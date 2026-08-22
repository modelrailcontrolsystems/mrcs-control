"""
Created on 21 Aug 2026

@author: Bruno Beloff (bbeloff@me.com)

The state of a command station
"""

from typing import Self

from mrcs_core.data.json import PersistentJSONable
from mrcs_core.equipment.control_router.control_router_report import ControlRouterReport


# --------------------------------------------------------------------------------------------------------------------

class PersistentControlRouter(ControlRouterReport, PersistentJSONable):
    """
     the state of a command station
     """

    __FILENAME = "control_router.json"


    @classmethod
    def persistence_location(cls):
        return cls.conf_dir(), cls.__FILENAME


    @classmethod
    def narrow(cls, report: ControlRouterReport) -> Self:
        return cls(report.main_current, report.prog_current, report.filtered_main_current,
                   report.supply_voltage, report.track_voltage, report.temperature,
                   report.central_state, report.central_state_ext, report.capabilities, report.reserved)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, main_current: int, prog_current: int, filtered_main_current: int,
                 supply_voltage: int, track_voltage: int, temperature: int,
                 central_state: int, central_state_ext: int, capabilities: int, reserved: int | None):
        super().__init__(main_current, prog_current, filtered_main_current,
                         supply_voltage, track_voltage, temperature,
                         central_state, central_state_ext, capabilities, reserved)
