"""
Created on 29 Aug 2026

@author: Bruno Beloff (bbeloff@me.com)
"""

import unittest
from unittest.mock import MagicMock

from mrcs_control.messaging.mq_client import MQManager, MQSubscriber
from mrcs_control.messaging.mq_topology import MQMode, MQTopology
from mrcs_core.data.equipment_identity import EquipmentIdentifier, EquipmentType


# --------------------------------------------------------------------------------------------------------------------

class TestMQClient(unittest.TestCase):

    def test_mq_client_close(self):
        manager = MQManager()
        mock_channel = MagicMock()
        mock_connection = MagicMock()

        manager.channel = mock_channel
        manager.connection = mock_connection

        result = manager.close()
        self.assertTrue(result)
        mock_channel.close.assert_called_once()
        mock_connection.close.assert_called_once()
        self.assertFalse(manager.is_connected)
        self.assertIsNone(manager.channel)
        self.assertIsNone(manager.connection)


    def test_mq_client_is_connected(self):
        manager = MQManager()
        self.assertFalse(manager.is_connected)

        manager.channel = MagicMock()
        self.assertTrue(manager.is_connected)

        manager.channel = None
        self.assertFalse(manager.is_connected)


    def test_mq_manager_queue_declare_no_channel(self):
        manager = MQManager()
        with self.assertRaises(RuntimeError):
            manager.queue_declare('test_queue')


    def test_mq_manager_queue_declare_success(self):
        manager = MQManager()
        mock_channel = MagicMock()
        manager.channel = mock_channel

        manager.queue_declare('test_queue', durable=True)
        mock_channel.queue_declare.assert_called_once_with(
            queue='test_queue',
            durable=True,
            exclusive=False,
            auto_delete=False,
        )


    def test_mq_manager_queue_purge_no_channel(self):
        manager = MQManager()
        with self.assertRaises(RuntimeError):
            manager.queue_purge('test_queue')


    def test_mq_manager_queue_purge_success(self):
        manager = MQManager()
        mock_channel = MagicMock()
        mock_response = MagicMock()
        mock_response.method.message_count = 5
        mock_channel.queue_purge.return_value = mock_response

        manager.channel = mock_channel

        purged = manager.queue_purge('test_queue')
        self.assertEqual(5, purged)
        mock_channel.queue_purge.assert_called_once_with('test_queue')


    def test_mq_subscriber_queue_purge_no_channel(self):
        subscriber = MQSubscriber(
            MQMode.TEST,
            MQTopology.QueueConfiguration(False, True, False),
            EquipmentIdentifier(EquipmentType.TRN, None, 1),
            lambda msg: None
        )
        with self.assertRaises(RuntimeError):
            subscriber.queue_purge()


    def test_mq_subscriber_queue_purge_success(self):
        subscriber = MQSubscriber(
            MQMode.TEST,
            MQTopology.QueueConfiguration(False, True, False),
            EquipmentIdentifier(EquipmentType.TRN, None, 1),
            lambda msg: None
        )
        mock_channel = MagicMock()
        mock_response = MagicMock()
        mock_response.method.message_count = 12
        mock_channel.queue_purge.return_value = mock_response

        subscriber.channel = mock_channel

        purged = subscriber.queue_purge()
        self.assertEqual(12, purged)
        mock_channel.queue_declare.assert_called_once_with(
            subscriber.queue_name,
            durable=subscriber.queue_config.durable,
            exclusive=subscriber.queue_config.exclusive,
        )
        mock_channel.queue_purge.assert_called_once_with(subscriber.queue_name)


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
