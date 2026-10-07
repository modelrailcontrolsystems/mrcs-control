"""
Created on 6 Jun 2026

@author: Bruno Beloff (bbeloff@me.com)

https://realpython.com/command-line-interfaces-python-argparse/
"""

from mrcs_control.cli.args.layout_actions import LayoutBlockReportAction, LayoutPlatformPathAction, \
    LayoutSegmentPathAction, LayoutStationReportAction

from mrcs_core.cli.args.multimode_args import MultimodeArgs
from mrcs_core.data.dot import Dot
from mrcs_core.equipment.block.block_enums import BlockHeading
from mrcs_core.layout.platform.platform_location import PlatformLocation
from mrcs_core.layout.segment.segment_location import SegmentLocation


# --------------------------------------------------------------------------------------------------------------------

class LayoutArgs(MultimodeArgs):
    """unix command line handler"""


    def __init__(self, description):
        super().__init__(description)

        group = self._parser.add_mutually_exclusive_group(required=True)

        group.add_argument('-l', '--list', action='store_true', help='list all layouts')

        group.add_argument('-sl', '--set-selected-layout', action='store', type=str, metavar='LAYOUT',
                           help='set selected layout')

        group.add_argument('-ba', '--block-abstract', action='store_true', help='print block abstract')

        group.add_argument('-ta', '--turnout-abstract', action='store_true', help='print turnout abstract')

        group.add_argument('-bv', '--block-view', action=LayoutBlockReportAction, type=str, nargs='?', const='*',
                           metavar='BLK[.SEG]', help='print block(s) with segment(s)')

        group.add_argument('-sv', '--station-view', action=LayoutStationReportAction, type=str, nargs='?', const='*',
                           metavar='STN[.PLT]', help='print station(s) with platform(s)')

        group.add_argument('-sr', '--segment-route', action=LayoutSegmentPathAction, nargs=3,
                           metavar=('HEADING', 'BLK1.SEG1', 'BLK2.SEG2'),
                           help='find path with HEADING: { UP | DN } from BLK1.SEG1 to BLK2.SEG2')

        group.add_argument('-pr', '--platform-route', action=LayoutPlatformPathAction, nargs=3,
                           metavar=('HEADING', 'STN1.PLT1', 'STN2.PLT2'),
                           help='find path with HEADING: { UP | DN } from STN1.PLT1 to STN2.PLT2')

        self._args = self._parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def list(self):
        return self._args.list


    @property
    def set_selected_layout(self):
        return self._args.set_selected_layout


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def block_abstract(self):
        return self._args.block_abstract


    @property
    def turnout_abstract(self):
        return self._args.turnout_abstract


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def block_view(self):
        return self._args.block_view is not None


    @property
    def view_node_block(self):
        return Dot.node(self._args.block_view, 0)


    @property
    def view_node_segment(self):
        return Dot.node(self._args.block_view, 1)


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def station_view(self):
        return self._args.station_view is not None


    @property
    def view_node_station(self):
        return Dot.node(self._args.station_view, 0)


    @property
    def view_node_platform(self):
        node = Dot.node(self._args.station_view, 1)
        return None if node is None else int(node)


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def route_heading(self):
        if self._args.segment_route:
            return BlockHeading.UP if self._args.segment_route[0] == 'UP' else BlockHeading.DOWN

        if self._args.platform_route:
            return BlockHeading.UP if self._args.platform_route[0] == 'UP' else BlockHeading.DOWN

        return None


    @property
    def segment_route(self):
        return self._args.segment_route


    @property
    def segment_route_start(self):
        if self._args.segment_route is None:
            return None
        return SegmentLocation.construct_from_dot_path(self._args.segment_route[1])


    @property
    def segment_route_end(self):
        if self._args.segment_route is None:
            return None
        return SegmentLocation.construct_from_dot_path(self._args.segment_route[2])


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def platform_route(self):
        return self._args.platform_route


    @property
    def platform_route_start(self):
        if self._args.platform_route is None:
            return None
        return PlatformLocation.construct_from_dot_path(self._args.platform_route[1])


    @property
    def platform_route_end(self):
        if self._args.platform_route is None:
            return None
        return PlatformLocation.construct_from_dot_path(self._args.platform_route[2])


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'LayoutArgs:{{list:{self.list}, set_selected_layout:{self.set_selected_layout}, '
                f'block_abstract:{self.block_abstract}, turnout_abstract:{self.turnout_abstract}, '
                f'block_view:{self.block_view}, station_view:{self.station_view}, '
                f'segment_route:{self.segment_route}, platform_route:{self.platform_route}, '
                f'indent:{self.indent}, verbose:{self.verbose}}}')
