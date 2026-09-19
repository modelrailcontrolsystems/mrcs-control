"""
Created on 16 Sep 2026

@author: Bruno Beloff (bbeloff@me.com)

https://realpython.com/command-line-interfaces-python-argparse/
"""

from argparse import Action


# --------------------------------------------------------------------------------------------------------------------

class MPUDriveAction(Action):
    """argparse action for MPU drive command (ADDR DIR SPEED)"""


    def __call__(self, parser, namespace, values, option_string=None):
        if values is None:
            return

        opt = option_string if option_string else '-s/--set-mpu-drive'

        try:
            addr = int(values[0])
        except ValueError:
            parser.error(f"argument {opt}: ADDR must be an integer (got '{values[0]}')")

        direction = values[1].upper()
        if direction not in ('FWD', 'REV'):
            parser.error(f"argument {opt}: DIR must be 'FWD' or 'REV' (got '{values[1]}')")

        try:
            speed = int(values[2])
            if not (0 <= speed <= 255):
                raise ValueError
        except ValueError:
            parser.error(f"argument {opt}: SPEED must be an integer in range 0-255 (got '{values[2]}')")

        setattr(namespace, self.dest, (addr, direction, speed))
