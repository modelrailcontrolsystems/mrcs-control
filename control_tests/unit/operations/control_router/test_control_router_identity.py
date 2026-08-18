"""
Created on 9 Aug 2026

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v unit/equipment/control_router/test_control_router_identity.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import unittest

from mrcs_control.operations.control_router.control_router_identity import ControlRouterIdentity
from mrcs_core.equipment.block.block_enums import BlockVoltage
from mrcs_core.equipment.block.block_id import BlockID
from mrcs_core.equipment.block.block_report import BlockOccupancyReport, BlockVoltageReport
from mrcs_core.equipment.control_router.control_router_report import ControlRouterReport
from mrcs_core.equipment.motive_power_unit.mpu_configuration_report import MPUConfigurationReport
from mrcs_core.equipment.motive_power_unit.mpu_decoder_report import MPUDecoderReport
from mrcs_core.equipment.motive_power_unit.mpu_enums import ThrottleSteps
from mrcs_core.equipment.motive_power_unit.mpu_functions import MPUFunctions
from mrcs_core.equipment.track.track_enums import TrackMode
from mrcs_core.equipment.track.track_report import TrackReport
from mrcs_core.equipment.turnout.turnout_enums import TurnoutPosition
from mrcs_core.equipment.turnout.turnout_report import TurnoutReport


# --------------------------------------------------------------------------------------------------------------------

class TestControlRouterIdentity(unittest.TestCase):

    def test_identity_common(self):
        obj1 = BlockID(1, 2, 3)
        obj2 = ControlRouterIdentity.get(obj1)
        self.assertEqual('EquipmentIdentifier:{equipment_type:CRT, sector_number:None, serial_number:Unclassified{2}}',
                         str(obj2))


    def test_identity_system(self):
        obj1 = ControlRouterReport(1, 2, 3, 4, 5,
                                   6, 7, 8, 9, None)
        obj2 = ControlRouterIdentity.get(obj1)
        self.assertEqual('EquipmentIdentifier:{equipment_type:CRT, sector_number:None, serial_number:System{4}}',
                         str(obj2))


    def test_identity_block_cccupancy(self):
        obj1 = BlockOccupancyReport(BlockID(1, 2, 3), 1, [])
        obj2 = ControlRouterIdentity.get(obj1)
        self.assertEqual('EquipmentIdentifier:{equipment_type:CRT, sector_number:None, serial_number:Track{5}}',
                         str(obj2))


    def test_identity_block_voltage(self):
        obj1 = BlockVoltageReport(BlockID(1, 2, 3), BlockVoltage.FREE_NO_VOLTAGE)
        obj2 = ControlRouterIdentity.get(obj1)
        self.assertEqual('EquipmentIdentifier:{equipment_type:CRT, sector_number:None, serial_number:Track{5}}',
                         str(obj2))


    def test_identity_mpu_decoder(self):
        obj1 = MPUDecoderReport(1, 2, 3, 4, 5, 6)
        obj2 = ControlRouterIdentity.get(obj1)
        self.assertEqual('EquipmentIdentifier:{equipment_type:CRT, sector_number:None, serial_number:MPU{7}}',
                         str(obj2))


    def test_identity_mpu_configuration(self):
        obj1 = MPUConfigurationReport(1, MPUFunctions([]), False, ThrottleSteps.STEPS_128,
                                      1, False, False, False)
        obj2 = ControlRouterIdentity.get(obj1)
        self.assertEqual('EquipmentIdentifier:{equipment_type:CRT, sector_number:None, serial_number:MPU{7}}',
                         str(obj2))


    def test_identity_mpu_track(self):
        obj1 = TrackReport(TrackMode.POWER_OFF)
        obj2 = ControlRouterIdentity.get(obj1)
        self.assertEqual('EquipmentIdentifier:{equipment_type:CRT, sector_number:None, serial_number:Track{5}}',
                         str(obj2))


    def test_identity_turnout(self):
        obj1 = TurnoutReport(1, TurnoutPosition.P1)
        obj2 = ControlRouterIdentity.get(obj1)
        self.assertEqual('EquipmentIdentifier:{equipment_type:CRT, sector_number:None, serial_number:Track{5}}',
                         str(obj2))
