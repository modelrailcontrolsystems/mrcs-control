"""
Created on 16 Nov 2025

@author: Bruno Beloff (bbeloff@me.com)

A universal message logger
"""

from mrcs_control.db.db_client import DbClient
from mrcs_control.operations.messaging_node import SubscriberNode
from mrcs_control.operations.operation_mode import OperationService
from mrcs_control.operations.recorder.message_record import PersistentMessageRecord
from mrcs_control.operations.recorder.persistent_message import PersistentMessage

from mrcs_core.data.equipment_identity import EquipmentIdentifier, EquipmentFilter, EquipmentType
from mrcs_core.data.json import JSONify
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import SubscriptionRoutingKey


# --------------------------------------------------------------------------------------------------------------------

class MessageRecorder(SubscriberNode):
    """
    A universal message logger
    """

    @classmethod
    def identity(cls):
        return EquipmentIdentifier(EquipmentType.MLG, None, 1)


    @classmethod
    def subscription_routing_keys(cls):
        return (SubscriptionRoutingKey(EquipmentFilter.all(), EquipmentFilter.all()), )


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: OperationService):
        super().__init__(ops)


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


    # ----------------------------------------------------------------------------------------------------------------

    def handle(self, message: Message):
        self.logger.info(f'handle: {JSONify.as_jdict(message)}')

        message = PersistentMessage.widen(message)
        message.save()

