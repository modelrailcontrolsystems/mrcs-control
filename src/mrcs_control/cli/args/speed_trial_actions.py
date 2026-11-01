"""
Created on 3 Oct 2026

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

class SpeedTrialSingleRunAction(Action):
    """
    argparse action for speed trial --single-run command (MPU BLOCK SPEED)
    """


    def __call__(self, parser, namespace, values, option_string=None):
        if values is None:
            return

        opt = option_string if option_string else '-s/--single-run'

        try:
            Valid.int(values[2], min_value=2, max_value=127)
        except ValueError:
            parser.error(f"argument {opt}: VALUE must be 2 to 127 (got '{values[2]}')")

        setattr(namespace, self.dest, (str(values[0]), str(values[1]), int(values[2])))
