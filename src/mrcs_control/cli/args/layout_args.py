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
from mrcs_core.inventory.platform.platform_location import PlatformLocation
from mrcs_core.inventory.segment.segment_location import SegmentLocation


# --------------------------------------------------------------------------------------------------------------------

class LayoutArgs(MultimodeArgs):
    """unix command line handler"""


    def __init__(self, description):
        super().__init__(description)

        group = self._parser.add_mutually_exclusive_group(required=True)

        group.add_argument('-l', '--list', action='store_true', help='list all layouts')

        group.add_argument('-sl', '--set-selected-layout', action='store', type=str, metavar='LAYOUT',
                           help='set selected layout')

        group.add_argument('-br', '--block-report', action=LayoutBlockReportAction, type=str, nargs='?', const='*',
                           metavar='BLK[.SEG]', help='print block(s) with segment(s)')

        group.add_argument('-sr', '--station-report', action=LayoutStationReportAction, type=str, nargs='?', const='*',
                           metavar='STN[.PLT]', help='print station(s) with platform(s)')

        group.add_argument('-sp', '--segment-path', action=LayoutSegmentPathAction, nargs=3,
                           metavar=('HEADING', 'BLK1.SEG1', 'BLK2.SEG2'),
                           help='find path with HEADING: { UP | DN } from BLK1.SEG1 to BLK2.SEG2')

        group.add_argument('-pp', '--platform-path', action=LayoutPlatformPathAction, nargs=3,
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
    def block_report(self):
        return self._args.block_report is not None


    @property
    def report_node_block(self):
        return Dot.node(self._args.block_report, 0)


    @property
    def report_node_segment(self):
        return Dot.node(self._args.block_report, 1)


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def station_report(self):
        return self._args.station_report is not None


    @property
    def report_node_station(self):
        return Dot.node(self._args.station_report, 0)


    @property
    def report_node_platform(self):
        node = Dot.node(self._args.station_report, 1)  # validated by LayoutStationReportAction
        return None if node is None else int(node)


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
        return SegmentLocation.construct_from_dot_path(self._args.segment_path[1])


    @property
    def segment_path_end(self):
        if self._args.segment_path is None:
            return None
        return SegmentLocation.construct_from_dot_path(self._args.segment_path[2])


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def platform_path(self):
        return self._args.platform_path


    @property
    def platform_path_start(self):
        if self._args.platform_path is None:
            return None
        return PlatformLocation.construct_from_dot_path(self._args.platform_path[1])


    @property
    def platform_path_end(self):
        if self._args.platform_path is None:
            return None
        return PlatformLocation.construct_from_dot_path(self._args.platform_path[2])


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (
            f'LayoutArgs:{{list:{self.list}, set_selected_layout:{self.set_selected_layout}, '
            f'block_report:{self.block_report}, station_report:{self.station_report}, '
            f'segment_path:{self.segment_path}, platform_path:{self.platform_path}, '
            f'indent:{self.indent}, verbose:{self.verbose}}}')
