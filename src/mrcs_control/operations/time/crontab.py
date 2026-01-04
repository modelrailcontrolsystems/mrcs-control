"""
Created on 31 Dec 2025

@author: Bruno Beloff (bbeloff@me.com)

Message-based Cron - this component accepts event schedules
Note that the cron components work in model time, not true time.
"""

from mrcs_control.db.db_client import DbClient
from mrcs_control.operations.messaging_node import SubscriberNode
from mrcs_control.operations.operation_mode import OperationService
from mrcs_control.operations.time.persistent_cronjob import PersistentCronjob

from mrcs_core.data.equipment_identity import EquipmentIdentifier, EquipmentFilter, EquipmentType
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import SubscriptionRoutingKey


# --------------------------------------------------------------------------------------------------------------------

class Crontab(SubscriberNode):
    """
    accepts event schedules
    """

    @classmethod
    def identity(cls):
        return EquipmentIdentifier(EquipmentType.CRN, None, 1)


    @classmethod
    def routing_key(cls):
        source = EquipmentFilter.all()
        target = EquipmentFilter(EquipmentType.CRN, None, None)

        return SubscriptionRoutingKey(source, target)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: OperationService):
        super().__init__(ops)


    # ----------------------------------------------------------------------------------------------------------------

    def callback(self, message: Message):
        cronjob = PersistentCronjob.construct_from_message(message)
        cronjob.save()

        self.logger.info(f'callback: {cronjob}')


    # ----------------------------------------------------------------------------------------------------------------

    def clean(self):
        DbClient.set_client_db_mode(self.ops.db_mode)
        PersistentCronjob.recreate_tables()


    def find_all(self):
        DbClient.set_client_db_mode(self.ops.db_mode)
        PersistentCronjob.create_tables()

        return PersistentCronjob.find_all()


    def subscribe(self):
        DbClient.set_client_db_mode(self.ops.db_mode)
        PersistentCronjob.create_tables()

        self.mq_client.connect()

        try:
            self.mq_client.subscribe(self.routing_key())
        except KeyboardInterrupt:
            return
