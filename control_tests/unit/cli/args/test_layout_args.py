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
from mrcs_core.inventory.layout.location import Location
from mrcs_core.inventory.platform.platform_label import PlatformLabel


# --------------------------------------------------------------------------------------------------------------------

class TestLayoutArgs(unittest.TestCase):

    # Mode flags -----------------------------------------------------------------------------------------------------

    def test_list(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-l']):
            args = LayoutArgs('test')
            self.assertTrue(args.list)
            self.assertIsNone(args.report)
            self.assertIsNone(args.set_selected_layout)
            self.assertIsNone(args.segment_path)
            self.assertIsNone(args.platform_path)
            self.assertIsNone(args.path_heading)


    def test_report(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-r', 'shelf_001']):
            args = LayoutArgs('test')
            self.assertFalse(args.list)
            self.assertEqual('shelf_001', args.report)
            self.assertIsNone(args.set_selected_layout)
            self.assertIsNone(args.segment_path)
            self.assertIsNone(args.platform_path)
            self.assertIsNone(args.path_heading)


    def test_set_selected_layout(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-s', 'shelf_001']):
            args = LayoutArgs('test')
            self.assertFalse(args.list)
            self.assertIsNone(args.report)
            self.assertEqual('shelf_001', args.set_selected_layout)
            self.assertIsNone(args.segment_path)
            self.assertIsNone(args.platform_path)
            self.assertIsNone(args.path_heading)


    def test_no_arguments(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    # Segment path ---------------------------------------------------------------------------------------------------

    def test_segment_path_up(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-g', 'UP', 'B1/S1', 'B2/S2']):
            args = LayoutArgs('test')
            self.assertFalse(args.list)
            self.assertIsNone(args.report)
            self.assertIsNone(args.set_selected_layout)
            self.assertEqual(('UP', 'B1/S1', 'B2/S2'), args.segment_path)
            self.assertEqual(BlockHeading.UP, args.path_heading)
            self.assertEqual(Location('B1', 'S1'), args.segment_path_start)
            self.assertEqual(Location('B2', 'S2'), args.segment_path_end)
            self.assertIsNone(args.platform_path)
            self.assertIsNone(args.platform_path_start)
            self.assertIsNone(args.platform_path_end)


    def test_segment_path_down_lowercase(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-g', 'dn', 'B1/S1', 'B2/S2']):
            args = LayoutArgs('test')
            self.assertEqual(('DN', 'B1/S1', 'B2/S2'), args.segment_path)
            self.assertEqual(BlockHeading.DOWN, args.path_heading)
            self.assertEqual(Location('B1', 'S1'), args.segment_path_start)
            self.assertEqual(Location('B2', 'S2'), args.segment_path_end)


    def test_segment_path_invalid_heading(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-g', 'X', 'B1/S1', 'B2/S2']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    def test_segment_path_invalid_start(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-g', 'UP', 'B1', 'B2/S2']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    def test_segment_path_invalid_end(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-g', 'UP', 'B1/S1', 'B2']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    def test_segment_path_missing_argument(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-g', 'UP', 'B1/S1']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    # Platform path --------------------------------------------------------------------------------------------------

    def test_platform_path_up(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-p', 'UP', 'Station/1', 'Station/2']):
            args = LayoutArgs('test')
            self.assertFalse(args.list)
            self.assertIsNone(args.report)
            self.assertIsNone(args.set_selected_layout)
            self.assertEqual(('UP', 'Station/1', 'Station/2'), args.platform_path)
            self.assertEqual(BlockHeading.UP, args.path_heading)
            self.assertEqual(PlatformLabel('Station', 1), args.platform_path_start)
            self.assertEqual(PlatformLabel('Station', 2), args.platform_path_end)
            self.assertIsNone(args.segment_path)
            self.assertIsNone(args.segment_path_start)
            self.assertIsNone(args.segment_path_end)


    def test_platform_path_down_lowercase(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-p', 'dn', 'Station/1', 'Station/2']):
            args = LayoutArgs('test')
            self.assertEqual(('DN', 'Station/1', 'Station/2'), args.platform_path)
            self.assertEqual(BlockHeading.DOWN, args.path_heading)
            self.assertEqual(PlatformLabel('Station', 1), args.platform_path_start)
            self.assertEqual(PlatformLabel('Station', 2), args.platform_path_end)


    def test_platform_path_invalid_heading(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-p', 'X', 'Station/1', 'Station/2']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    def test_platform_path_invalid_start(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-p', 'UP', 'Station', 'Station/2']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    def test_platform_path_invalid_end(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-p', 'UP', 'Station/1', 'Station']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    def test_platform_path_missing_argument(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-p', 'UP', 'Station/1']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    # Actions --------------------------------------------------------------------------------------------------------

    def test_segment_path_action_none_values(self):
        action = LayoutSegmentPathAction(option_strings=['-g', '--segment-path'], dest='segment_path')
        parser = ArgumentParser()
        namespace = Namespace()
        action(parser, namespace, None)
        self.assertFalse(hasattr(namespace, 'segment_path'))


    def test_platform_path_action_none_values(self):
        action = LayoutPlatformPathAction(option_strings=['-p', '--platform-path'], dest='platform_path')
        parser = ArgumentParser()
        namespace = Namespace()
        action(parser, namespace, None)
        self.assertFalse(hasattr(namespace, 'platform_path'))


    # String representation ------------------------------------------------------------------------------------------

    def test_str(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', '-g', 'UP', 'B1/S1', 'B2/S2']):
            args = LayoutArgs('test')
            self.assertEqual(
                "LayoutArgs:{list:False, report:None, set_selected_layout:None, "
                "segment_path:('UP', 'B1/S1', 'B2/S2'), platform_path:None, "
                "indent:None, verbose:False}", str(args))


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
