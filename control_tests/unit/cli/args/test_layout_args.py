"""
Created on 16 Sep 2026

@author: Bruno Beloff (bbeloff@me.com)
"""

import sys
import unittest
from argparse import ArgumentParser, Namespace
from unittest.mock import patch

from mrcs_control.cli.args.layout_actions import LayoutBlockReportAction, LayoutPlatformPathAction, \
    LayoutSegmentPathAction, LayoutStationReportAction
from mrcs_control.cli.args.layout_args import LayoutArgs
from mrcs_core.equipment.block.block_enums import BlockHeading
from mrcs_core.inventory.platform.platform_location import PlatformLocation
from mrcs_core.inventory.segment.segment_location import SegmentLocation


# --------------------------------------------------------------------------------------------------------------------

class TestLayoutArgs(unittest.TestCase):

    # Mode flags -----------------------------------------------------------------------------------------------------

    def test_list(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-l']):
            args = LayoutArgs('test')
            self.assertTrue(args.list)
            self.assertIsNone(args.set_selected_layout)
            self.assertFalse(args.block_view)
            self.assertFalse(args.station_view)
            self.assertIsNone(args.segment_route)
            self.assertIsNone(args.platform_route)
            self.assertIsNone(args.route_heading)


    def test_set_selected_layout(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-sl', 'shelf_001']):
            args = LayoutArgs('test')
            self.assertFalse(args.list)
            self.assertEqual('shelf_001', args.set_selected_layout)
            self.assertFalse(args.block_view)
            self.assertFalse(args.station_view)
            self.assertIsNone(args.segment_route)
            self.assertIsNone(args.platform_route)
            self.assertIsNone(args.route_heading)


    def test_no_arguments(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    def test_mutually_exclusive(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-l', '-bv']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    # Block report ---------------------------------------------------------------------------------------------------

    def test_block_view_all(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-bv']):
            args = LayoutArgs('test')
            self.assertFalse(args.list)
            self.assertIsNone(args.set_selected_layout)
            self.assertTrue(args.block_view)
            self.assertIsNone(args.view_node_block)
            self.assertIsNone(args.view_node_segment)
            self.assertFalse(args.station_view)
            self.assertIsNone(args.segment_route)
            self.assertIsNone(args.platform_route)


    def test_block_view_wildcard(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-bv', '*']):
            args = LayoutArgs('test')
            self.assertTrue(args.block_view)
            self.assertIsNone(args.view_node_block)
            self.assertIsNone(args.view_node_segment)


    def test_block_view_block(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-bv', 'BS01']):
            args = LayoutArgs('test')
            self.assertTrue(args.block_view)
            self.assertEqual('BS01', args.view_node_block)
            self.assertIsNone(args.view_node_segment)


    def test_block_view_block_segment(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-bv', 'BS01.SG02']):
            args = LayoutArgs('test')
            self.assertTrue(args.block_view)
            self.assertEqual('BS01', args.view_node_block)
            self.assertEqual('SG02', args.view_node_segment)


    def test_block_view_too_many_arguments(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-bv', 'BS01', 'SG02']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    def test_block_view_too_many_nodes(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-bv', 'BS01.SG02.X']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    # Station report -------------------------------------------------------------------------------------------------

    def test_station_view_all(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-sv']):
            args = LayoutArgs('test')
            self.assertFalse(args.list)
            self.assertIsNone(args.set_selected_layout)
            self.assertFalse(args.block_view)
            self.assertTrue(args.station_view)
            self.assertIsNone(args.view_node_station)
            self.assertIsNone(args.view_node_platform)
            self.assertIsNone(args.segment_route)
            self.assertIsNone(args.platform_route)


    def test_station_view_wildcard(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-sv', '*']):
            args = LayoutArgs('test')
            self.assertTrue(args.station_view)
            self.assertIsNone(args.view_node_station)
            self.assertIsNone(args.view_node_platform)


    def test_station_view_station(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-sv', 'TST']):
            args = LayoutArgs('test')
            self.assertTrue(args.station_view)
            self.assertEqual('TST', args.view_node_station)
            self.assertIsNone(args.view_node_platform)


    def test_station_view_station_platform(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-sv', 'TST.1']):
            args = LayoutArgs('test')
            self.assertTrue(args.station_view)
            self.assertEqual('TST', args.view_node_station)
            self.assertEqual(1, args.view_node_platform)


    def test_station_view_station_platform_not_integer(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-sv', 'TST.x']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    def test_station_view_station_platform_empty(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-sv', 'TST.']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    def test_station_view_too_many_arguments(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-sv', 'TST', '1']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    def test_station_view_too_many_nodes(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-sv', 'TST.1.X']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    # Segment path ---------------------------------------------------------------------------------------------------

    def test_segment_route_up(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-sr', 'UP', 'B1.S1', 'B2.S2']):
            args = LayoutArgs('test')
            self.assertFalse(args.list)
            self.assertIsNone(args.set_selected_layout)
            self.assertFalse(args.block_view)
            self.assertFalse(args.station_view)
            self.assertEqual(('UP', 'B1.S1', 'B2.S2'), args.segment_route)
            self.assertEqual(BlockHeading.UP, args.route_heading)
            self.assertEqual(SegmentLocation('B1', 'S1'), args.segment_route_start)
            self.assertEqual(SegmentLocation('B2', 'S2'), args.segment_route_end)
            self.assertIsNone(args.platform_route)
            self.assertIsNone(args.platform_route_start)
            self.assertIsNone(args.platform_route_end)


    def test_segment_route_down_lowercase(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-sr', 'dn', 'B1.S1', 'B2.S2']):
            args = LayoutArgs('test')
            self.assertEqual(('DN', 'B1.S1', 'B2.S2'), args.segment_route)
            self.assertEqual(BlockHeading.DOWN, args.route_heading)
            self.assertEqual(SegmentLocation('B1', 'S1'), args.segment_route_start)
            self.assertEqual(SegmentLocation('B2', 'S2'), args.segment_route_end)


    def test_segment_route_invalid_heading(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-sr', 'X', 'B1.S1', 'B2.S2']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    def test_segment_route_invalid_start(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-sr', 'UP', 'B1', 'B2.S2']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    def test_segment_route_invalid_end(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-sr', 'UP', 'B1.S1', 'B2']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    def test_segment_route_too_many_nodes(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-sr', 'UP', 'B1.S1.X', 'B2.S2']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')

        with patch.object(sys, 'argv', ['mrcs_control_layout', '-sr', 'UP', 'B1.S1', 'B2.S2.X']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    def test_segment_route_missing_argument(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-sr', 'UP', 'B1.S1']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    # Platform path --------------------------------------------------------------------------------------------------

    def test_platform_route_up(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-pr', 'UP', 'Station.1', 'Station.2']):
            args = LayoutArgs('test')
            self.assertFalse(args.list)
            self.assertIsNone(args.set_selected_layout)
            self.assertFalse(args.block_view)
            self.assertFalse(args.station_view)
            self.assertEqual(('UP', 'Station.1', 'Station.2'), args.platform_route)
            self.assertEqual(BlockHeading.UP, args.route_heading)
            self.assertEqual(PlatformLocation('Station', 1), args.platform_route_start)
            self.assertEqual(PlatformLocation('Station', 2), args.platform_route_end)
            self.assertIsNone(args.segment_route)
            self.assertIsNone(args.segment_route_start)
            self.assertIsNone(args.segment_route_end)


    def test_platform_route_down_lowercase(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-pr', 'dn', 'Station.1', 'Station.2']):
            args = LayoutArgs('test')
            self.assertEqual(('DN', 'Station.1', 'Station.2'), args.platform_route)
            self.assertEqual(BlockHeading.DOWN, args.route_heading)
            self.assertEqual(PlatformLocation('Station', 1), args.platform_route_start)
            self.assertEqual(PlatformLocation('Station', 2), args.platform_route_end)


    def test_platform_route_invalid_heading(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-pr', 'X', 'Station.1', 'Station.2']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    def test_platform_route_invalid_start(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-pr', 'UP', 'Station', 'Station.2']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    def test_platform_route_invalid_end(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-pr', 'UP', 'Station.1', 'Station']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    def test_platform_route_too_many_nodes(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-pr', 'UP', 'Station.1.X', 'Station.2']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')

        with patch.object(sys, 'argv', ['mrcs_control_layout', '-pr', 'UP', 'Station.1', 'Station.2.X']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    def test_platform_route_missing_argument(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-pr', 'UP', 'Station.1']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    # Actions --------------------------------------------------------------------------------------------------------

    def test_segment_route_action_none_values(self):
        action = LayoutSegmentPathAction(option_strings=['-sr', '--segment-path'], dest='segment_route')
        parser = ArgumentParser()
        namespace = Namespace()
        action(parser, namespace, None)
        self.assertFalse(hasattr(namespace, 'segment_route'))


    def test_platform_route_action_none_values(self):
        action = LayoutPlatformPathAction(option_strings=['-pr', '--platform-path'], dest='platform_route')
        parser = ArgumentParser()
        namespace = Namespace()
        action(parser, namespace, None)
        self.assertFalse(hasattr(namespace, 'platform_route'))


    def test_station_view_action_none_values(self):
        action = LayoutStationReportAction(option_strings=['-sv', '--station-report'], dest='station_view')
        parser = ArgumentParser()
        namespace = Namespace()
        action(parser, namespace, None)
        self.assertFalse(hasattr(namespace, 'station_view'))


    def test_station_view_action_stores_values(self):
        action = LayoutStationReportAction(option_strings=['-sv', '--station-report'], dest='station_view')
        parser = ArgumentParser()
        namespace = Namespace()
        action(parser, namespace, 'TST.1')
        self.assertEqual('TST.1', namespace.station_view)


    def test_block_view_action_none_values(self):
        action = LayoutBlockReportAction(option_strings=['-bv', '--block-report'], dest='block_view')
        parser = ArgumentParser()
        namespace = Namespace()
        action(parser, namespace, None)
        self.assertFalse(hasattr(namespace, 'block_view'))


    def test_block_view_action_stores_values(self):
        action = LayoutBlockReportAction(option_strings=['-bv', '--block-report'], dest='block_view')
        parser = ArgumentParser()
        namespace = Namespace()
        action(parser, namespace, 'BS01.SG02')
        self.assertEqual('BS01.SG02', namespace.block_view)


    # String representation ------------------------------------------------------------------------------------------

    def test_str(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-sr', 'UP', 'B1.S1', 'B2.S2']):
            args = LayoutArgs('test')
            self.assertEqual("LayoutArgs:{list:False, set_selected_layout:None, block_inventory:False, "
                             "turnout_inventory:False, block_view:False, station_view:False, "
                             "segment_route:('UP', 'B1.S1', 'B2.S2'), platform_route:None, "
                             "indent:None, verbose:False}", str(args))


    def test_str_block_view(self):
        self.maxDiff = None
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-bv', 'BS01.SG02']):
            args = LayoutArgs('test')
            self.assertEqual("LayoutArgs:{list:False, set_selected_layout:None, block_inventory:False, "
                             "turnout_inventory:False, block_view:True, station_view:False, segment_route:None, "
                             "platform_route:None, indent:None, verbose:False}", str(args))


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
