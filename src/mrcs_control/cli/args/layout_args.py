"""
Created on 6 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

https://realpython.com/command-line-interfaces-python-argparse/
"""

from argparse import Action

from mrcs_core.cli.args.multimode_args import MultimodeArgs
from mrcs_core.equipment.block.block_enums import BlockHeading
from mrcs_core.inventory.layout.location import Location


# --------------------------------------------------------------------------------------------------------------------

class PathAction(Action):
    """argparse action for layout path command (HEADING B1 S1 B2 S2)"""


    def __call__(self, parser, namespace, values, option_string=None):
        if values is None:
            return

        opt = option_string if option_string else '-p/--path'

        heading = values[0].upper()
        if heading not in ('UP', 'DN'):
            parser.error(f"argument {opt}: HEADING must be 'UP' or 'DN' (got '{values[0]}')")

        try:
            Location.construct_from_shortform(values[1])
        except ValueError:
            parser.error(f"argument {opt}: START is malformed' (got '{values[1]}')")

        try:
            Location.construct_from_shortform(values[2])
        except ValueError:
            parser.error(f"argument {opt}: END is malformed' (got '{values[2]}')")

        setattr(namespace, self.dest, (heading, values[1], values[2]))


# --------------------------------------------------------------------------------------------------------------------

class LayoutArgs(MultimodeArgs):
    """unix command line handler"""


    def __init__(self, description):
        super().__init__(description)

        self._parser.add_argument('layout', action='store', type=str, help='layout name')

        group = self._parser.add_mutually_exclusive_group(required=False)

        group.add_argument('-p', '--path', action=PathAction, nargs=3, metavar=('HEADING', 'START', 'END'),
                           help='find path from B1/S1 to B2/S2 for HEADING: { UP | DN }')

        self._args = self._parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def layout(self):
        return self._args.layout


    @property
    def path(self):
        return self._args.path


    @property
    def path_heading(self):
        if self._args.path is None:
            return None
        return BlockHeading.UP if self._args.path[0] == 'UP' else BlockHeading.DOWN


    @property
    def path_start(self):
        return None if self._args.path is None else Location.construct_from_shortform(self._args.path[1])


    @property
    def path_end(self):
        return None if self._args.path is None else Location.construct_from_shortform(self._args.path[2])


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'LayoutArgs:{{layout:{self.layout}, path:{self.path}, '
                f'indent:{self.indent}, verbose:{self.verbose}}}')
