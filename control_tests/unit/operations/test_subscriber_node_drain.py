"""
Created on 29 Aug 2026

@author: Bruno Beloff (bbeloff@me.com)
"""

import sys
import unittest
from unittest.mock import MagicMock, patch

from mrcs_control.cli.args.clock_conf_args import ClockConfArgs
from mrcs_control.cli.args.clock_manager_args import ClockManagerArgs
from mrcs_control.cli.args.command_args import CommandArgs
from mrcs_control.cli.args.cron_args import CronArgs
from mrcs_control.cli.args.crontab_args import CrontabArgs
from mrcs_control.cli.args.recorder_args import RecorderArgs
from mrcs_control.cli.args.router_args import RouterArgs
from mrcs_control.cli.args.track_args import TrackArgs
from mrcs_control.cli.internal.topic_subscriber_node import TopicSubscriberNode
from mrcs_control.operations.node_topology import NodeTopology
from mrcs_control.operations.time.cron_node import CronNode
from mrcs_control.operations.track.track_node import TrackNode


# --------------------------------------------------------------------------------------------------------------------

class TestSubscriberNodeDrain(unittest.TestCase):

    @patch('mrcs_control.operations.async_messaging_node.MQManager')
    def test_track_node_drain(self, mock_mq_manager_class):
        mock_manager = MagicMock()
        mock_manager.queue_purge.return_value = 7
        mock_mq_manager_class.return_value = mock_manager

        node = TrackNode(NodeTopology.TEST.value)
        purged = node.drain()

        self.assertEqual(7, purged)
        mock_manager.connect.assert_called_once()
        mock_manager.queue_declare.assert_called_once_with(
            node.mq_client.queue_name,
            durable=node.mq_client.queue_config.durable,
            exclusive=node.mq_client.queue_config.exclusive,
        )
        mock_manager.queue_purge.assert_called_once_with(node.mq_client.queue_name)
        mock_manager.close.assert_called_once()


    @patch('mrcs_control.operations.async_messaging_node.MQManager')
    def test_subscriber_node_drain_exclusive(self, mock_mq_manager_class):
        mock_mq_client = MagicMock()
        mock_mq_client.queue_config.exclusive = True

        node = TrackNode(NodeTopology.TEST.value)
        node.mq_client = mock_mq_client

        purged = node.drain()
        self.assertIsNone(purged)
        mock_mq_manager_class.assert_not_called()


    @patch('mrcs_control.operations.async_messaging_node.MQManager')
    def test_topic_subscriber_node_drain_exclusive(self, mock_mq_manager_class):
        node = TopicSubscriberNode.construct_node(NodeTopology.TEST.value, lambda msg: None)
        purged = node.drain()

        self.assertIsNone(purged)
        mock_mq_manager_class.assert_not_called()


    @patch('mrcs_control.operations.async_messaging_node.MQManager')
    def test_cron_node_drain(self, mock_mq_manager_class):
        mock_manager = MagicMock()
        mock_manager.queue_purge.return_value = 5
        mock_mq_manager_class.return_value = mock_manager

        node = CronNode(NodeTopology.TEST.value, save_model_time=False)
        purged = node.drain()

        self.assertEqual(5, purged)
        mock_manager.connect.assert_called_once()
        mock_manager.queue_declare.assert_called_once_with(
            node.mq_client.queue_name,
            durable=node.mq_client.queue_config.durable,
            exclusive=node.mq_client.queue_config.exclusive,
        )
        mock_manager.queue_purge.assert_called_once_with(node.mq_client.queue_name)
        mock_manager.close.assert_called_once()


    @patch('mrcs_control.operations.async_messaging_node.MQManager')
    def test_cron_node_drain_no_channel(self, mock_mq_manager_class):
        mock_manager = MagicMock()
        mock_manager.queue_declare.side_effect = RuntimeError('queue_declare: no channel')
        mock_mq_manager_class.return_value = mock_manager

        node = CronNode(NodeTopology.TEST.value, save_model_time=False)
        with self.assertRaises(RuntimeError):
            node.drain()

        mock_manager.close.assert_called_once()


    def test_track_args_with_drain(self):
        with patch.object(sys, 'argv', ['mrcs_control_track', '-t', '-d', '-r']):
            args = TrackArgs('test')
            self.assertTrue(args.test)
            self.assertTrue(args.drain)
            self.assertTrue(args.run)
            self.assertIsNone(args.list)
            self.assertFalse(args.populate)


    def test_track_args_without_drain(self):
        with patch.object(sys, 'argv', ['mrcs_control_track', '-t', '-r']):
            args = TrackArgs('test')
            self.assertTrue(args.test)
            self.assertFalse(args.drain)
            self.assertTrue(args.run)

    def test_cron_args_with_drain(self):
        with patch.object(sys, 'argv', ['mrcs_control_cron', '-t', '-d', '-r']):
            args = CronArgs('test')
            self.assertTrue(args.test)
            self.assertTrue(args.drain)
            self.assertTrue(args.run)
            self.assertIn('drain:True', str(args))

    def test_crontab_args_with_drain(self):
        with patch.object(sys, 'argv', ['mrcs_control_crontab', '-t', '-d', '-s']):
            args = CrontabArgs('test')
            self.assertTrue(args.test)
            self.assertTrue(args.drain)
            self.assertTrue(args.subscribe)
            self.assertIn('drain:True', str(args))

    def test_recorder_args_with_drain(self):
        with patch.object(sys, 'argv', ['mrcs_control_recorder', '-t', '-d', '-s']):
            args = RecorderArgs('test')
            self.assertTrue(args.test)
            self.assertTrue(args.drain)
            self.assertTrue(args.subscribe)
            self.assertIn('drain:True', str(args))

    def test_router_args_with_drain(self):
        with patch.object(sys, 'argv', ['mrcs_control_router', '-t', '-d', '-r']):
            args = RouterArgs('test')
            self.assertTrue(args.test)
            self.assertTrue(args.drain)
            self.assertTrue(args.run)
            self.assertIn('drain:True', str(args))

    def test_clock_manager_args_with_drain(self):
        with patch.object(sys, 'argv', ['mrcs_control_clock_manager', '-t', '-d', '-s']):
            args = ClockManagerArgs('test')
            self.assertTrue(args.test)
            self.assertTrue(args.drain)
            self.assertTrue(args.subscribe)
            self.assertIn('drain:True', str(args))

    def test_clock_conf_args_with_drain(self):
        with patch.object(sys, 'argv', ['mrcs_control_clock_conf', '-t', '-d', '-n']):
            args = ClockConfArgs('test')
            self.assertTrue(args.test)
            self.assertTrue(args.drain)
            self.assertTrue(args.now)
            self.assertIn('drain:True', str(args))

    def test_command_args_with_drain(self):
        with patch.object(sys, 'argv', ['mrcs_control_command', '-t', '-d', '-m']):
            args = CommandArgs('test')
            self.assertTrue(args.test)
            self.assertTrue(args.drain)
            self.assertTrue(args.monitor)
            self.assertIn('drain:True', str(args))


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
