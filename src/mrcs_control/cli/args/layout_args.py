"""
Created on 6 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

https://realpython.com/command-line-interfaces-python-argparse/
"""

from argparse import Action

from mrcs_core.cli.args.multimode_args import MultimodeArgs
from mrcs_core.equipment.block.block_enums import BlockHeading
from mrcs_core.inventory.layout.location import Location
from mrcs_core.inventory.platform.platform_label import PlatformLabel


# --------------------------------------------------------------------------------------------------------------------

class SegmentPathAction(Action):
    """
    argparse action for layout segment-path command (HEADING Station1/1 Station2/2)
    """


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


class PlatformPathAction(Action):
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


# --------------------------------------------------------------------------------------------------------------------

class LayoutArgs(MultimodeArgs):
    """unix command line handler"""


    def __init__(self, description):
        super().__init__(description)

        self._parser.add_argument('layout', action='store', type=str, help='layout name')

        group = self._parser.add_mutually_exclusive_group(required=False)

        group.add_argument('-s', '--segment-path', action=SegmentPathAction, nargs=3,
                           metavar=('HEADING', 'START', 'END'),
                           help='find path from B1/S1 to B2/S2 for HEADING: { UP | DN }')

        group.add_argument('-p', '--platform-path', action=PlatformPathAction, nargs=3,
                           metavar=('HEADING', 'START', 'END'),
                           help='find path from Station/1 to Station/2 for HEADING: { UP | DN }')

        self._args = self._parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def layout(self):
        return self._args.layout


    @property
    def path_heading(self):
        if self._args.segment_path:
            return BlockHeading.UP if self._args.segment_path[0] == 'UP' else BlockHeading.DOWN

        if self._args.platform_path:
            return BlockHeading.UP if self._args.platform_path[0] == 'UP' else BlockHeading.DOWN

        return None


    @property
    def segment_path(self):
        return self._args.segment_path


    @property
    def segment_path_start(self):
        if self._args.segment_path is None:
            return None
        return Location.construct_from_shortform(self._args.segment_path[1])


    @property
    def segment_path_end(self):
        if self._args.segment_path is None:
            return None
        return Location.construct_from_shortform(self._args.segment_path[2])


    @property
    def platform_path(self):
        return self._args.platform_path


    @property
    def platform_path_start(self):
        if self._args.platform_path is None:
            return None
        return PlatformLabel.construct_from_shortform(self._args.platform_path[1])


    @property
    def platform_path_end(self):
        if self._args.platform_path is None:
            return None
        return PlatformLabel.construct_from_shortform(self._args.platform_path[2])


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'LayoutArgs:{{layout:{self.layout}, segment_path:{self.segment_path}, '
                f'platform_path:{self.platform_path}, indent:{self.indent}, verbose:{self.verbose}}}')
