"""
Created on 16 Nov 2025

@author: Bruno Beloff (bbeloff@me.com)

A universal message logger
"""

from typing import List

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
        return EquipmentIdentifier(EquipmentType.REC, None, 1)


    @classmethod
    def subscription_routing_keys(cls) -> list[SubscriptionRoutingKey]:
        return [SubscriptionRoutingKey(EquipmentFilter.any(), EquipmentFilter.any())]


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: NodeTopology.ServiceConfiguration):
        super().__init__(ops, MQTopology.SINGLE_PROCESS)


    # ----------------------------------------------------------------------------------------------------------------

    def handle_message(self, message: Message):
        self.logger.info(f'handle_message: {JSONify.as_jdict(message)}')

        message = PersistentMessage.narrow(message)
        message.save()


    # ----------------------------------------------------------------------------------------------------------------

    def clean(self) -> None:
        DbClient.set_client_db_mode(self.ops.db_mode)
        PersistentMessageRecord.recreate_tables()


    def find_latest(self, limit: int) -> List[PersistentMessageRecord]:
        self.__setup()
        return PersistentMessageRecord.find_latest(limit)


    def subscribe(self) -> None:
        self.__setup()

        if not self.mq_client.is_connected:
            self.mq_client.connect()
            self.logger.info('subscribed')

        try:
            self.mq_client.subscribe(*self.subscription_routing_keys())
        except KeyboardInterrupt:
            return


    def __setup(self):
        DbClient.set_client_db_mode(self.ops.db_mode)
        PersistentMessageRecord.create_tables()
