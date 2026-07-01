"""
Created on 10 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

A DCC motive power unit (MPU) state, as reported by a Z21 DCC command station

Classes in support of the Rocco Z21 DCC command station:
https://www.z21.eu/en/products/z21

Based on code:
https://github.com/botmonster/z21aio/tree/main
https://gitlab.com/z21-fpm/z21_python
"""

from mrcs_control.dcc.z21.command.dataset import Dataset
from mrcs_core.equipment.motive_power_unit.mpu_configuration_report import MPUConfigurationReport
from mrcs_core.equipment.motive_power_unit.throttle import DCCThrottleSteps


# --------------------------------------------------------------------------------------------------------------------

class Z21MPUConfigurationReport(object):
    """
    A DCC motive power unit (MPU) state, as reported by a Z21 DCC command station
    """


    @classmethod
    def construct_from_dataset(cls, dataset: Dataset) -> MPUConfigurationReport:
        data = dataset.data

        if len(data) < 2:
            raise ValueError(f'Z21MPUConfigurationReport data requires at least 2 bytes, got {data.hex(" ")}')

        address = ((data[0] & 0x3f) << 8) | data[1]
        functions = [False] * 32

        mpu_config = MPUConfigurationReport(address, functions)

        try:
            byte = 2
            mpu_config._is_busy = bool(data[byte] & 0x08)

            try:
                mpu_config._stepping = DCCThrottleSteps(data[2] & 0x07)
            except ValueError:
                pass

            byte = 3
            mpu_config._reverse = not bool(data[byte] & 0x80)
            mpu_config._speed_setting = data[byte] & 0x7F

            byte = 4
            mpu_config._double_traction = bool(data[byte] & 0x40)
            mpu_config._smart_search = bool(data[byte] & 0x20)

            mpu_config.functions[0] = bool(data[byte] & 0x10)

            for bit in range(4):
                mpu_config.functions[1 + bit] = cls.__extract_bool(data[byte], bit)

            for offset in range(5, 30, 8):
                byte += 1
                for bit in range(8):
                    mpu_config.functions[offset + bit] = cls.__extract_bool(data[byte], bit)

        except IndexError:
            pass

        return mpu_config


    @staticmethod
    def __extract_bool(byte, bit) -> bool:
        return bool(byte & (1 << bit))
