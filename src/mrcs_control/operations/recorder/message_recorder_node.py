"""
Created on 16 Nov 2025

@author: Bruno Beloff (bbeloff@me.com)

A universal message logger
"""

from mrcs_control.db.db_client import DbClient
from mrcs_control.messaging.mq_topology import MQTopology
from mrcs_control.operations.messaging_node import SubscriberNode
from mrcs_control.operations.node_topology import NodeTopology
from mrcs_control.operations.recorder.persistent_message import PersistentMessage
from mrcs_control.operations.recorder.persistent_message_record import PersistentMessageRecord
from mrcs_core.data.equipment_identity import EquipmentFilter, EquipmentIdentifier, EquipmentType
from mrcs_core.data.json import JSONify
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import SubscriptionRoutingKey


# --------------------------------------------------------------------------------------------------------------------

class MessageRecorderNode(SubscriberNode):
    """
    A universal message logger
    """


    @classmethod
    def id(cls):
        return EquipmentIdentifier(EquipmentType.MLG, None, 1)


    @classmethod
    def subscription_routing_keys(cls):
        return (SubscriptionRoutingKey(EquipmentFilter.any(), EquipmentFilter.any()),)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: NodeTopology.ServiceConfiguration):
        super().__init__(ops, MQTopology.SINGLE)


    # ----------------------------------------------------------------------------------------------------------------

    def handle_message(self, message: Message):
        self.logger.info(f'handle_message: {JSONify.as_jdict(message)}')

        message = PersistentMessage.narrow(message)
        message.save()


    # ----------------------------------------------------------------------------------------------------------------

    def clean(self):
        DbClient.set_client_db_mode(self.ops.db_mode)
        PersistentMessageRecord.recreate_tables()


    def find_latest(self, limit: int):
        DbClient.set_client_db_mode(self.ops.db_mode)
        PersistentMessageRecord.create_tables()

        return PersistentMessageRecord.find_latest(limit)


    def subscribe(self):
        DbClient.set_client_db_mode(self.ops.db_mode)
        PersistentMessageRecord.create_tables()

        self.mq_client.connect()

        try:
            self.mq_client.subscribe(*self.subscription_routing_keys())
        except KeyboardInterrupt:
            return
