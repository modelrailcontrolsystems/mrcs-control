"""
Created on 16 Sep 2026

@author: Bruno Beloff (bbeloff@me.com)
"""

import sys
import unittest
from argparse import ArgumentParser, Namespace
from unittest.mock import patch

from mrcs_control.cli.args.layout_args import LayoutArgs
from mrcs_control.cli.args.layout_platform_path_action import LayoutPlatformPathAction
from mrcs_control.cli.args.layout_segment_path_action import LayoutSegmentPathAction
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
            self.assertFalse(args.segment_report)
            self.assertFalse(args.platform_report)
            self.assertIsNone(args.segment_path)
            self.assertIsNone(args.platform_path)
            self.assertIsNone(args.path_heading)


    def test_set_selected_layout(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-sl', 'shelf_001']):
            args = LayoutArgs('test')
            self.assertFalse(args.list)
            self.assertEqual('shelf_001', args.set_selected_layout)
            self.assertFalse(args.segment_report)
            self.assertFalse(args.platform_report)
            self.assertIsNone(args.segment_path)
            self.assertIsNone(args.platform_path)
            self.assertIsNone(args.path_heading)


    def test_no_arguments(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    def test_mutually_exclusive(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-l', '-sl']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    # Block report ---------------------------------------------------------------------------------------------------

    def test_segment_report_all(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-sr']):
            args = LayoutArgs('test')
            self.assertFalse(args.list)
            self.assertIsNone(args.set_selected_layout)
            self.assertTrue(args.segment_report)
            self.assertIsNone(args.report_node_block)
            self.assertIsNone(args.report_node_segment)
            self.assertFalse(args.platform_report)
            self.assertIsNone(args.segment_path)
            self.assertIsNone(args.platform_path)


    def test_segment_report_wildcard(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-sr', '*']):
            args = LayoutArgs('test')
            self.assertTrue(args.segment_report)
            self.assertIsNone(args.report_node_block)
            self.assertIsNone(args.report_node_segment)


    def test_segment_report_block(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-sr', 'BS01']):
            args = LayoutArgs('test')
            self.assertTrue(args.segment_report)
            self.assertEqual('BS01', args.report_node_block)
            self.assertIsNone(args.report_node_segment)


    def test_segment_report_block_segment(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-sr', 'BS01.SG02']):
            args = LayoutArgs('test')
            self.assertTrue(args.segment_report)
            self.assertEqual('BS01', args.report_node_block)
            self.assertEqual('SG02', args.report_node_segment)


    def test_segment_report_too_many_arguments(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-sr', 'BS01', 'SG02']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    # Station report -------------------------------------------------------------------------------------------------

    def test_platform_report_all(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-pr']):
            args = LayoutArgs('test')
            self.assertFalse(args.list)
            self.assertIsNone(args.set_selected_layout)
            self.assertFalse(args.segment_report)
            self.assertTrue(args.platform_report)
            self.assertIsNone(args.report_node_station)
            self.assertIsNone(args.report_node_platform)
            self.assertIsNone(args.segment_path)
            self.assertIsNone(args.platform_path)


    def test_platform_report_wildcard(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-pr', '*']):
            args = LayoutArgs('test')
            self.assertTrue(args.platform_report)
            self.assertIsNone(args.report_node_station)
            self.assertIsNone(args.report_node_platform)


    def test_platform_report_station(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-pr', 'TST']):
            args = LayoutArgs('test')
            self.assertTrue(args.platform_report)
            self.assertEqual('TST', args.report_node_station)
            self.assertIsNone(args.report_node_platform)


    def test_platform_report_station_platform(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-pr', 'TST.1']):
            args = LayoutArgs('test')
            self.assertTrue(args.platform_report)
            self.assertEqual('TST', args.report_node_station)
            self.assertEqual(1, args.report_node_platform)


    def test_platform_report_too_many_arguments(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-pr', 'TST', '1']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    # Segment path ---------------------------------------------------------------------------------------------------

    def test_segment_path_up(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-sp', 'UP', 'B1.S1', 'B2.S2']):
            args = LayoutArgs('test')
            self.assertFalse(args.list)
            self.assertIsNone(args.set_selected_layout)
            self.assertFalse(args.segment_report)
            self.assertFalse(args.platform_report)
            self.assertEqual(('UP', 'B1.S1', 'B2.S2'), args.segment_path)
            self.assertEqual(BlockHeading.UP, args.path_heading)
            self.assertEqual(SegmentLocation('B1', 'S1'), args.segment_path_start)
            self.assertEqual(SegmentLocation('B2', 'S2'), args.segment_path_end)
            self.assertIsNone(args.platform_path)
            self.assertIsNone(args.platform_path_start)
            self.assertIsNone(args.platform_path_end)


    def test_segment_path_down_lowercase(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-sp', 'dn', 'B1.S1', 'B2.S2']):
            args = LayoutArgs('test')
            self.assertEqual(('DN', 'B1.S1', 'B2.S2'), args.segment_path)
            self.assertEqual(BlockHeading.DOWN, args.path_heading)
            self.assertEqual(SegmentLocation('B1', 'S1'), args.segment_path_start)
            self.assertEqual(SegmentLocation('B2', 'S2'), args.segment_path_end)


    def test_segment_path_invalid_heading(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-sp', 'X', 'B1.S1', 'B2.S2']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    def test_segment_path_invalid_start(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-sp', 'UP', 'B1', 'B2.S2']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    def test_segment_path_invalid_end(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-sp', 'UP', 'B1.S1', 'B2']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    def test_segment_path_missing_argument(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-sp', 'UP', 'B1.S1']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    # Platform path --------------------------------------------------------------------------------------------------

    def test_platform_path_up(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-pp', 'UP', 'Station.1', 'Station.2']):
            args = LayoutArgs('test')
            self.assertFalse(args.list)
            self.assertIsNone(args.set_selected_layout)
            self.assertFalse(args.segment_report)
            self.assertFalse(args.platform_report)
            self.assertEqual(('UP', 'Station.1', 'Station.2'), args.platform_path)
            self.assertEqual(BlockHeading.UP, args.path_heading)
            self.assertEqual(PlatformLocation('Station', 1), args.platform_path_start)
            self.assertEqual(PlatformLocation('Station', 2), args.platform_path_end)
            self.assertIsNone(args.segment_path)
            self.assertIsNone(args.segment_path_start)
            self.assertIsNone(args.segment_path_end)


    def test_platform_path_down_lowercase(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-pp', 'dn', 'Station.1', 'Station.2']):
            args = LayoutArgs('test')
            self.assertEqual(('DN', 'Station.1', 'Station.2'), args.platform_path)
            self.assertEqual(BlockHeading.DOWN, args.path_heading)
            self.assertEqual(PlatformLocation('Station', 1), args.platform_path_start)
            self.assertEqual(PlatformLocation('Station', 2), args.platform_path_end)


    def test_platform_path_invalid_heading(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-pp', 'X', 'Station.1', 'Station.2']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    def test_platform_path_invalid_start(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-pp', 'UP', 'Station', 'Station.2']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    def test_platform_path_invalid_end(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-pp', 'UP', 'Station.1', 'Station']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    def test_platform_path_missing_argument(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-pp', 'UP', 'Station.1']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    # Actions --------------------------------------------------------------------------------------------------------

    def test_segment_path_action_none_values(self):
        action = LayoutSegmentPathAction(option_strings=['-sp', '--segment-path'], dest='segment_path')
        parser = ArgumentParser()
        namespace = Namespace()
        action(parser, namespace, None)
        self.assertFalse(hasattr(namespace, 'segment_path'))


    def test_platform_path_action_none_values(self):
        action = LayoutPlatformPathAction(option_strings=['-pp', '--platform-path'], dest='platform_path')
        parser = ArgumentParser()
        namespace = Namespace()
        action(parser, namespace, None)
        self.assertFalse(hasattr(namespace, 'platform_path'))


    # String representation ------------------------------------------------------------------------------------------

    def test_str(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-sp', 'UP', 'B1.S1', 'B2.S2']):
            args = LayoutArgs('test')
            self.assertEqual(
                "LayoutArgs:{list:False, set_selected_layout:None, segment_report:False, platform_report:False, "
                "segment_path:('UP', 'B1.S1', 'B2.S2'), platform_path:None, "
                "indent:None, verbose:False}", str(args))


    def test_str_segment_report(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-sr', 'BS01.SG02']):
            args = LayoutArgs('test')
            self.assertEqual(
                "LayoutArgs:{list:False, set_selected_layout:None, segment_report:True, platform_report:False, "
                "segment_path:None, platform_path:None, "
                "indent:None, verbose:False}", str(args))


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
