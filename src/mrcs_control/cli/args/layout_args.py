"""
Created on 6 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

https://realpython.com/command-line-interfaces-python-argparse/
"""

from mrcs_control.cli.args.layout_platform_path_action import LayoutPlatformPathAction
from mrcs_control.cli.args.layout_segment_path_action import LayoutSegmentPathAction

from mrcs_core.cli.args.multimode_args import MultimodeArgs
from mrcs_core.equipment.block.block_enums import BlockHeading
from mrcs_core.inventory.layout.location import Location
from mrcs_core.inventory.platform.platform_label import PlatformLabel


# --------------------------------------------------------------------------------------------------------------------

class LayoutArgs(MultimodeArgs):
    """unix command line handler"""


    def __init__(self, description):
        super().__init__(description)

        group = self._parser.add_mutually_exclusive_group(required=True)

        group.add_argument('-l', '--list', action='store_true', help='list all layouts')

        group.add_argument('-r', '--report', action='store', type=str, metavar='LAYOUT', help='print LAYOUT')

        group.add_argument('-s', '--set-selected-layout', action='store', type=str, metavar='LAYOUT',
                           help='set selected layout')

        group.add_argument('-g', '--segment-path', action=LayoutSegmentPathAction, nargs=3,
                           metavar=('HEADING', 'START', 'END'),
                           help='find path from B1/S1 to B2/S2 for HEADING: { UP | DN }')

        group.add_argument('-p', '--platform-path', action=LayoutPlatformPathAction, nargs=3,
                           metavar=('HEADING', 'START', 'END'),
                           help='find path from Station/1 to Station/2 for HEADING: { UP | DN }')

        self._args = self._parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def list(self):
        return self._args.list


    @property
    def report(self):
        return self._args.report


    @property
    def set_selected_layout(self):
        return self._args.set_selected_layout


    # ----------------------------------------------------------------------------------------------------------------

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
        return (
            f'LayoutArgs:{{list:{self.list}, report:{self.report}, set_selected_layout:{self.set_selected_layout}, '
            f'segment_path:{self.segment_path}, platform_path:{self.platform_path}, '
            f'indent:{self.indent}, verbose:{self.verbose}}}')
