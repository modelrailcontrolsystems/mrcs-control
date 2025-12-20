"""
Created on 16 Nov 2025

@author: Bruno Beloff (bbeloff@me.com)

A universal message logger
"""

from mrcs_control.db.dbclient import DBClient
from mrcs_control.messaging.mqclient import Subscriber
from mrcs_control.operations.operation_mode import OperationMode, OperationService
from mrcs_control.operations.recorder.message import PersistentMessage
from mrcs_control.operations.recorder.message_record import PersistentMessageRecord

from mrcs_core.data.equipment_identity import EquipmentIdentifier, EquipmentFilter, EquipmentType
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import SubscriptionRoutingKey
from mrcs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

class MessageRecorder(object):
    """
    A universal message logger
    """

    @classmethod
    def construct(cls, ops_mode: OperationMode):
        identity = EquipmentIdentifier(EquipmentType.MLG, None, 1)
        routing_key = SubscriptionRoutingKey(EquipmentFilter.all(), EquipmentFilter.all())

        return cls(identity, routing_key, ops_mode.value)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, identity: EquipmentIdentifier, routing_key: SubscriptionRoutingKey, ops: OperationService):
        self.__identity = identity
        self.__routing_key = routing_key
        self.__ops = ops

        self.__logger = Logging.getLogger()


    # ----------------------------------------------------------------------------------------------------------------

    def callback(self, message: Message):
        self.__logger.info(message)
        PersistentMessage.widen(message).save()


    # ----------------------------------------------------------------------------------------------------------------

    def clean(self):
        DBClient.set_client_db_mode(self.ops.db_mode)
        PersistentMessageRecord.recreate_tables()


    def find_latest(self, limit):
        self.__logger.warning("find_latest")
        DBClient.set_client_db_mode(self.ops.db_mode)
        return PersistentMessageRecord.find_latest(limit)


    def subscribe(self):
        DBClient.set_client_db_mode(self.ops.db_mode)
        PersistentMessageRecord.create_tables()

        endpoint = Subscriber.construct_sub(self.ops.mq_mode, self.identity, self.callback)
        endpoint.connect()

        try:
            endpoint.subscribe(self.routing_key)
        except KeyboardInterrupt:
            return


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def identity(self):
        return self.__identity


    @property
    def routing_key(self):
        return self.__routing_key


    @property
    def ops(self):
        return self.__ops


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'MessageRecorder:{{identity:{self.identity}, routing_key:{self.routing_key}, ops:{self.ops}}}'
