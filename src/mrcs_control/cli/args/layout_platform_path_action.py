"""
Created on 29 Sep 2026

@author: Bruno Beloff (bbeloff@me.com)

https://realpython.com/command-line-interfaces-python-argparse/
"""

from argparse import Action

from mrcs_core.inventory.platform.platform_label import PlatformLabel


# --------------------------------------------------------------------------------------------------------------------

class LayoutPlatformPathAction(Action):
    """
    argparse action for layout platform-path command (HEADING B1/S1 B2/S2)
    """


    def __call__(self, parser, namespace, values, option_string=None):
        if values is None:
            return

        opt = option_string if option_string else '-p/--path'

        heading = values[0].upper()
        if heading not in ('UP', 'DN'):
            parser.error(f"argument {opt}: HEADING must be 'UP' or 'DN' (got '{values[0]}')")

        try:
            PlatformLabel.construct_from_shortform(values[1])
        except ValueError:
            parser.error(f"argument {opt}: START is malformed' (got '{values[1]}')")

        try:
            PlatformLabel.construct_from_shortform(values[2])
        except ValueError:
            parser.error(f"argument {opt}: END is malformed' (got '{values[2]}')")

        setattr(namespace, self.dest, (heading, values[1], values[2]))
