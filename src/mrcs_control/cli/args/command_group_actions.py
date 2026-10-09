"""
Created on 9 Oct 2026

@author: Bruno Beloff (bbeloff@me.com)

https://realpython.com/command-line-interfaces-python-argparse/
"""

import builtins
from argparse import Action
from typing import Any


# --------------------------------------------------------------------------------------------------------------------

class Valid(object):
    """
    integer validation
    """


    @classmethod
    def int(cls, value: Any, min_value: builtins.int | None = None,
            max_value: builtins.int | None = None) -> builtins.int:
        int_value = builtins.int(value)

        if min_value is not None and int_value < min_value:
            raise ValueError

        if max_value is not None and int_value > max_value:
            raise ValueError

        return int_value


    @classmethod
    def natural_number(cls, value):
        return cls.int(value, min_value=1)


# --------------------------------------------------------------------------------------------------------------------

class MPUDriveAction(Action):
    """
    argparse action for MPU drive command (ADDR DIR SPEED)
    """


    def __call__(self, parser, namespace, values, option_string=None):
        if values is None:
            return

        opt = option_string if option_string else '-sm/--set-mpu-drive'

        try:
            addr = Valid.int(values[0], min_value=1)
        except ValueError:
            parser.error(f"argument {opt}: ADDR must be a positive integer (got '{values[0]}')")

        direction = values[1].upper()
        if direction not in ('FWD', 'REV'):
            parser.error(f"argument {opt}: DIR must be 'FWD' or 'REV' (got '{values[1]}')")

        try:
            speed = Valid.int(values[2], min_value=0, max_value=255)
        except ValueError:
            parser.error(f"argument {opt}: SPEED must be an integer in range 0-255 (got '{values[2]}')")

        setattr(namespace, self.dest, (addr, direction, speed))


# --------------------------------------------------------------------------------------------------------------------

class TurnoutAction(Action):
    """
    argparse action for turnout command (ADDR POS)
    """


    def __call__(self, parser, namespace, values, option_string=None):
        if values is None:
            return

        opt = option_string if option_string else '-st/--set-turnout'

        try:
            addr = Valid.int(values[0], min_value=1)
        except ValueError:
            parser.error(f"argument {opt}: ADDR must be a positive integer (got '{values[0]}')")

        try:
            pos = Valid.int(values[1], min_value=0, max_value=1)
        except ValueError:
            parser.error(f"argument {opt}: POS must be 0 or 1 (got '{values[1]}')")

        setattr(namespace, self.dest, (addr, pos))
