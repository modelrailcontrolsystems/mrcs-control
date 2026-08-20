"""
Created on 31 Dec 2025

@author: Bruno Beloff (bbeloff@me.com)

An SubscriberNode that provides a crontab service - this component accepts event schedules
Note that the cron components work in model time, not true time.

Test with:
mrcs_publisher -vti4 -t CRN -n 3 -m '{"event_id": "abc", "on": "1930-01-02T06:25:00.000+00:00"}'
"""
from typing import List

from mrcs_control.db.db_client import DbClient
from mrcs_control.messaging.mq_topology import MQTopology
from mrcs_control.operations.messaging_node import SubscriberNode
from mrcs_control.operations.node_topology import NodeTopology
from mrcs_control.operations.time.cron_serial import CronSerial
from mrcs_control.operations.time.persistent_cronjob import PersistentCronjob
from mrcs_core.data.equipment_identity import EquipmentFilter, EquipmentIdentifier, EquipmentType
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
        return EquipmentIdentifier(EquipmentType.CRN, None, CronSerial.Crontab)


    @classmethod
    def subscription_routing_keys(cls):
        return (SubscriptionRoutingKey(EquipmentFilter.any(), cls.id()),)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: NodeTopology.ServiceConfiguration):
        super().__init__(ops, MQTopology.SINGLE)


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

    def clean(self) -> None:
        DbClient.set_client_db_mode(self.ops.db_mode)
        PersistentCronjob.recreate_tables()


    def find_all(self) -> List[PersistentCronjob]:
        self.__setup()
        return PersistentCronjob.find_all()


    def subscribe(self) -> None:
        self.__setup()

        self.mq_client.connect()
        self.logger.info('subscribed')

        try:
            self.mq_client.subscribe(*self.subscription_routing_keys())
        except KeyboardInterrupt:
            return


    def __setup(self):
        DbClient.set_client_db_mode(self.ops.db_mode)
        PersistentCronjob.create_tables()
