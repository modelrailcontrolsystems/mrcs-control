"""
Created on 3 Oct 2026

@author: Bruno Beloff (bbeloff@me.com)

https://realpython.com/command-line-interfaces-python-argparse/
"""

from argparse import Action

from mrcs_core.data.dot import Dot
from mrcs_core.inventory.platform.platform_location import PlatformLocation
from mrcs_core.inventory.segment.segment_location import SegmentLocation


# --------------------------------------------------------------------------------------------------------------------

class LayoutBlockReportAction(Action):
    """
    argparse action for layout block-report command ([BLK[.SEG]])
    """


    def __call__(self, parser, namespace, values, option_string=None):
        if values is None:
            return

        opt = option_string if option_string else '-br/--block-report'

        # with nargs='?', values is a single str
        # noinspection PyTypeChecker
        if len(Dot.nodes(values)) > 2:
            parser.error(f"argument {opt}: must be of the form BLK[.SEG] (got '{values}')")

        setattr(namespace, self.dest, values)


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
            PlatformLocation.construct_from_dot_path(values[1])
        except ValueError:
            parser.error(f"argument {opt}: START is malformed' (got '{values[1]}')")

        try:
            PlatformLocation.construct_from_dot_path(values[2])
        except ValueError:
            parser.error(f"argument {opt}: END is malformed' (got '{values[2]}')")

        setattr(namespace, self.dest, (heading, values[1], values[2]))


# --------------------------------------------------------------------------------------------------------------------

class LayoutSegmentPathAction(Action):
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
            SegmentLocation.construct_from_dot_path(values[1])
        except ValueError:
            parser.error(f"argument {opt}: START is malformed' (got '{values[1]}')")

        try:
            SegmentLocation.construct_from_dot_path(values[2])
        except ValueError:
            parser.error(f"argument {opt}: END is malformed' (got '{values[2]}')")

        setattr(namespace, self.dest, (heading, values[1], values[2]))


# --------------------------------------------------------------------------------------------------------------------

class LayoutStationReportAction(Action):
    """
    argparse action for layout station-report command ([STN[.PLT]])
    """


    def __call__(self, parser, namespace, values, option_string=None):
        if values is None:
            return

        opt = option_string if option_string else '-sr/--station-report'

        # noinspection PyTypeChecker
        if len(Dot.nodes(values)) > 2:
            parser.error(f"argument {opt}: must be of the form STN[.PLT] (got '{values}')")

        # noinspection PyTypeChecker
        platform = Dot.node(values, 1)
        if platform is not None:
            try:
                int(platform)
            except ValueError:
                parser.error(f"argument {opt}: PLT must be an integer (got '{platform}')")

        setattr(namespace, self.dest, values)
