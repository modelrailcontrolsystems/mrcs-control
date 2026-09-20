"""
Created on 16 Sep 2026

@author: Bruno Beloff (bbeloff@me.com)
"""

import sys
import unittest
from argparse import ArgumentParser, Namespace
from unittest.mock import patch

from mrcs_control.cli.args.layout_args import LayoutArgs, PathAction
from mrcs_core.equipment.block.block_enums import BlockHeading
from mrcs_core.inventory.layout.location import Location


# --------------------------------------------------------------------------------------------------------------------

class TestLayoutArgs(unittest.TestCase):

    def test_path_up(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', 'shelf_001', '-p', 'UP', 'B1/S1', 'B2/S2']):
            args = LayoutArgs('test')
            self.assertEqual('shelf_001', args.layout)
            self.assertEqual(('UP', 'B1/S1', 'B2/S2'), args.path)
            self.assertEqual(BlockHeading.UP, args.path_heading)
            self.assertEqual(Location('B1', 'S1'), args.path_start)
            self.assertEqual(Location('B2', 'S2'), args.path_end)


    def test_path_down_lowercase(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', 'shelf_001', '-p', 'dn', 'B1/S1', 'B2/S2']):
            args = LayoutArgs('test')
            self.assertEqual('shelf_001', args.layout)
            self.assertEqual(('DN', 'B1/S1', 'B2/S2'), args.path)
            self.assertEqual(BlockHeading.DOWN, args.path_heading)
            self.assertEqual(Location('B1', 'S1'), args.path_start)
            self.assertEqual(Location('B2', 'S2'), args.path_end)


    def test_path_invalid_heading(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', 'shelf_001', '-p', 'X', 'B1/S1', 'B2/S2']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    def test_path_missing_argument(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', 'shelf_001', '-p', 'UP', 'B1/S1']):
            with self.assertRaises(SystemExit):
                LayoutArgs('test')


    def test_no_path(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', 'shelf_001']):
            args = LayoutArgs('test')
            self.assertEqual('shelf_001', args.layout)
            self.assertIsNone(args.path)
            self.assertIsNone(args.path_heading)
            self.assertIsNone(args.path_start)
            self.assertIsNone(args.path_end)


    def test_path_action_none_values(self):
        action = PathAction(option_strings=['-p', '--path'], dest='path')
        parser = ArgumentParser()
        namespace = Namespace()
        action(parser, namespace, None)
        self.assertFalse(hasattr(namespace, 'path'))


    def test_str(self):
        with patch.object(sys, 'argv', ['mrcs_control_layout', 'shelf_001', '-p', 'UP', 'B1/S1', 'B2/S2']):
            args = LayoutArgs('test')
            self.assertIn("layout:shelf_001", str(args))
            self.assertIn("path:('UP', 'B1/S1', 'B2/S2')", str(args))


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
