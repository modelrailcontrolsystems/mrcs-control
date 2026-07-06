"""
Created on 10 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

A motive power unit (MPU) configuration, as reported by a Z21 DCC command station

Classes in support of the Rocco Z21 DCC command station:
https://www.z21.eu/en/products/z21

Based on code:
https://github.com/botmonster/z21aio/tree/main
https://gitlab.com/z21-fpm/z21_python
"""

from mrcs_control.dcc.z21.command.dataset import Dataset
from mrcs_core.equipment.motive_power_unit.mpu_configuration_report import MPUConfigurationReport
from mrcs_core.equipment.motive_power_unit.mpu_enums import ThrottleSteps
from mrcs_core.equipment.motive_power_unit.mpu_functions import MPUFunctions


# --------------------------------------------------------------------------------------------------------------------

class Z21MPUConfigurationReport(object):
    """
    A motive power unit (MPU) configuration, as reported by a Z21 DCC command station
    """


    @classmethod
    def construct_from_dataset(cls, dataset: Dataset) -> MPUConfigurationReport:
        data = dataset.data

        if len(data) < 2:
            raise ValueError(f'Z21MPUConfigurationReport data requires at least 2 bytes, got {data.hex(" ")}')

        # defaults
        address = ((data[0] & 0x3f) << 8) | data[1]
        functions = [False] * 32
        is_busy = False
        stepping = ThrottleSteps.STEPS_128
        speed_setting = 0
        reverse = False
        double_traction = False
        smart_search = False

        try:
            byte = 2
            is_busy = bool(data[byte] & 0x08)

            try:
                stepping = ThrottleSteps(data[2] & 0x07)
            except ValueError:
                pass

            byte = 3
            reverse = not bool(data[byte] & 0x80)
            speed_setting = data[byte] & 0x7F

            byte = 4
            double_traction = bool(data[byte] & 0x40)
            smart_search = bool(data[byte] & 0x20)

            functions[0] = bool(data[byte] & 0x10)

            for bit in range(4):
                functions[1 + bit] = cls.__extract_bool(data[byte], bit)

            for offset in range(5, 30, 8):
                byte += 1
                for bit in range(8):
                    functions[offset + bit] = cls.__extract_bool(data[byte], bit)

        except IndexError:
            pass

        return MPUConfigurationReport(address, MPUFunctions(functions), is_busy, stepping, speed_setting, reverse,
                                      double_traction, smart_search)


    @staticmethod
    def __extract_bool(byte, bit) -> bool:
        return bool(byte & (1 << bit))
