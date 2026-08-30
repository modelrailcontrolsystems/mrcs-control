"""
Created on 29 Aug 2026

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v unit/dcc/z21/equipment/test_equipment_report.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import struct
import unittest

from mrcs_control.dcc.z21.command.dataset import Dataset, XDataset
from mrcs_control.dcc.z21.command.header import Header, XHeader
from mrcs_control.dcc.z21.equipment.equpiment_report import EquipmentReport
from mrcs_core.equipment.block.block_report import BlockVoltageReport
from mrcs_core.equipment.control_router.control_router_report import ControlRouterReport
from mrcs_core.equipment.motive_power_unit.mpu_configuration_report import MPUConfigurationReport
from mrcs_core.equipment.motive_power_unit.mpu_decoder_report import MPUDecoderReport
from mrcs_core.equipment.track.track_report import TrackReport
from mrcs_core.equipment.turnout.turnout_report import TurnoutReport


# --------------------------------------------------------------------------------------------------------------------

class TestEquipmentReport(unittest.TestCase):

    def test_construct_block_report(self):
        chars = bytes([0x0e, 0x00, 0xc4, 0x00, 0x78, 0xdb, 0x04, 0x00, 0x00, 0x01, 0x00, 0x11, 0x00, 0x00])
        dataset = Dataset.construct_from_bytes(chars)
        report = EquipmentReport.construct_from_dataset(dataset)

        self.assertIsInstance(report, BlockVoltageReport)
        self.assertEqual('BlockVoltageReport:{block_id:BlockID:{detector_address:5, channel:1, '
                         'reporter_id:0xdb78}, voltage:OCCUPIED_WITH_VOLTAGE}', str(report))


    def test_construct_control_router_report(self):
        chars = bytes([0x14, 0x00, 0x84, 0x00, 0x0c, 0x01, 0x00, 0x00, 0xce, 0x00, 0x1f, 0x00, 0x1f, 0x4e, 0x14, 0x37,
                       0x00, 0x20, 0x03, 0x79])
        dataset = Dataset.construct_from_bytes(chars)
        report = EquipmentReport.construct_from_dataset(dataset)

        self.assertIsInstance(report, ControlRouterReport)
        self.assertEqual('ControlRouterReport:{main_current:268, prog_current:0, filtered_main_current:206, '
                         'supply_voltage:19999, track_voltage:14100, temperature:31, central_state:0x00, '
                         'central_state_ext:0x20, capabilities:0x79, reserved:0x03}', str(report))


    def test_construct_mpu_decoder_report(self):
        data = struct.pack('<HLHBBBBB', 0x1234, 456, 789, 0, 0xab, 90, 5, 0)
        chars = struct.pack('<HH', len(data) + 4, Header.LAN_RAILCOM_DATA_CHANGED) + data
        dataset = Dataset.construct_from_bytes(chars)
        report = EquipmentReport.construct_from_dataset(dataset)

        self.assertIsInstance(report, MPUDecoderReport)
        self.assertEqual('MPUDecoderReport:{mpu_address:4660, receive_count:456, error_count:789, opts:0xab, '
                         'speed:90, qos:5}', str(report))


    def test_construct_mpu_configuration_report(self):
        chars = bytes([0x0f, 0x00, 0x40, 0x00, 0xef, 0x00, 0x04, 0x0c, 0xb5, 0x01, 0x00, 0x00, 0x00, 0x00, 0x53])
        dataset = Dataset.construct_from_bytes(chars)
        report = EquipmentReport.construct_from_dataset(dataset)

        self.assertIsInstance(report, MPUConfigurationReport)
        self.assertEqual('MPUConfigurationReport:{mpu_address:4, functions:-+------------------------------, '
                         'is_busy:True, stepping:STEPS_128, speed_setting:53, reverse:False, '
                         'double_traction:False, smart_search:False}', str(report))


    def test_construct_track_report(self):
        chars = bytes([0x07, 0x00, 0x40, 0x00, 0x61, 0x01, 0x60])
        dataset = Dataset.construct_from_bytes(chars)
        report = EquipmentReport.construct_from_dataset(dataset)

        self.assertIsInstance(report, TrackReport)
        self.assertEqual('TrackReport:{mode:POWER_ON}', str(report))


    def test_construct_turnout_report(self):
        chars = bytes([0x09, 0x00, 0x40, 0x00, 0x43, 0x00, 0x00, 0x01, 0x42])
        dataset = Dataset.construct_from_bytes(chars)
        report = EquipmentReport.construct_from_dataset(dataset)

        self.assertIsInstance(report, TurnoutReport)
        self.assertEqual('TurnoutReport:{turnout_address:1, position:P0}', str(report))


    def test_construct_unsupported_header(self):
        dataset = Dataset(Header.LAN_GET_SERIAL_NUMBER, b'\x00\x00\x00\x00')
        with self.assertRaises(TypeError):
            EquipmentReport.construct_from_dataset(dataset)


    def test_construct_unsupported_x_header(self):
        dataset = XDataset.construct_from_command(Header.LAN_X, XHeader.LAN_X_GET_VERSION_REPLY, b'')
        with self.assertRaises(TypeError):
            EquipmentReport.construct_from_dataset(dataset)


# --------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
