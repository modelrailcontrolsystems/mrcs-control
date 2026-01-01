"""
Created on 31 Dec 2025

@author: Bruno Beloff (bbeloff@me.com)

Message-based Cron - this component accepts event schedules
"""

from mrcs_control.db.dbclient import DBClient
from mrcs_control.messaging.mqclient import Subscriber
from mrcs_control.operations.operation_mode import OperationMode, OperationService
from mrcs_control.operations.time.persistent_cronjob import PersistentCronjob

from mrcs_core.data.equipment_identity import EquipmentIdentifier, EquipmentFilter, EquipmentType
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import SubscriptionRoutingKey
from mrcs_core.sys.logging import Logging


# TODO: we need a MessagingNode ABC?
# --------------------------------------------------------------------------------------------------------------------

class Crontab(object):
    """
    accepts event schedules
    """

    @classmethod
    def construct(cls, ops_mode: OperationMode):
        identity = EquipmentIdentifier(EquipmentType.CRN, None, 1)

        source = EquipmentFilter.all()
        target = EquipmentFilter(EquipmentType.CRN, None, None)
        routing_key = SubscriptionRoutingKey(source, target)

        return cls(identity, routing_key, ops_mode.value)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, identity: EquipmentIdentifier, routing_key: SubscriptionRoutingKey, ops: OperationService):
        self.__identity = identity
        self.__routing_key = routing_key
        self.__ops = ops

        self.__logger = Logging.getLogger()


    # ----------------------------------------------------------------------------------------------------------------

    def callback(self, message: Message):
        cronjob = PersistentCronjob.construct_from_message(message)
        self.__logger.info(f'callback - cronjob:{cronjob}')
        cronjob.save()


    # ----------------------------------------------------------------------------------------------------------------

    def clean(self):
        DBClient.set_client_db_mode(self.ops.db_mode)
        PersistentCronjob.recreate_tables()


    def find_all(self):
        DBClient.set_client_db_mode(self.ops.db_mode)
        PersistentCronjob.create_tables()

        return PersistentCronjob.find_all()


    def subscribe(self):
        DBClient.set_client_db_mode(self.ops.db_mode)
        PersistentCronjob.create_tables()

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
        return f'Crontab:{{identity:{self.identity}, routing_key:{self.routing_key}, ops:{self.ops}}}'
