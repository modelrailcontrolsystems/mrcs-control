"""
Created on 31 Dec 2025

@author: Bruno Beloff (bbeloff@me.com)

An SubscriberNode that provides a crontab service - this component accepts event schedules
Note that the cron components work in model time, not true time.

Test with:
mrcs_publisher -vti4 -t CRN -n 3 -m '{"event_id": "abc", "on": "1930-01-02T06:25:00.000+00:00"}'
"""

from mrcs_control.db.db_client import DbClient
from mrcs_control.operations.messaging_node import SubscriberNode
from mrcs_control.operations.operation_mode import OperationService
from mrcs_control.operations.time.cron import CRN
from mrcs_control.operations.time.persistent_cronjob import PersistentCronjob

from mrcs_core.data.equipment_identity import EquipmentIdentifier, EquipmentFilter, EquipmentType
from mrcs_core.data.json import JSONify
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import SubscriptionRoutingKey


# --------------------------------------------------------------------------------------------------------------------

class CrontabNode(SubscriberNode):
    """
    accepts event schedules
    """


    @classmethod
    def id(cls):
        return EquipmentIdentifier(EquipmentType.CRN, None, CRN.Crontab)


    @classmethod
    def subscription_routing_keys(cls):
        return (SubscriptionRoutingKey(EquipmentFilter.any(), cls.id()),)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: OperationService):
        super().__init__(ops)


    # ----------------------------------------------------------------------------------------------------------------

    def handle_message(self, message: Message):
        self.logger.info(f'handle_message: {JSONify.as_jdict(message)}')

        try:
            cronjob = PersistentCronjob.construct_from_message(message)
        except Exception:
            self.logger.warning(f'invalid message body:{message.body}')
            return

        cronjob.save()


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
            self.mq_client.subscribe(*self.subscription_routing_keys())
        except KeyboardInterrupt:
            return
