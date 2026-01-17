"""
Created on 17 Jan 2026

@author: Bruno Beloff (bbeloff@me.com)

Message-based Cron - this component raises events
Note that the cron components work in model time, not true time.
"""

from mrcs_control.operations.messaging_node import SubscriberNode
from mrcs_control.operations.operation_mode import OperationService

from mrcs_core.data.equipment_identity import EquipmentIdentifier, EquipmentType, EquipmentFilter
from mrcs_core.data.json import JSONify
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import SubscriptionRoutingKey, PublicationRoutingKey
from mrcs_core.operations.time.clock import Clock
from mrcs_core.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

class ClockManager(SubscriberNode):
    """
    raises events
    """

    @classmethod
    def identity(cls):
        return EquipmentIdentifier(EquipmentType.CRN, None, 1)


    @classmethod
    def subscription_routing_keys(cls):
        return (SubscriptionRoutingKey(EquipmentFilter.all(), cls.identity()), )


    @classmethod
    def publication_routing_key(cls):
        return PublicationRoutingKey(cls.identity(), EquipmentFilter.all())


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: OperationService):
        super().__init__(ops)


    # ----------------------------------------------------------------------------------------------------------------

    def subscribe(self):
        self.mq_client.connect()

        try:
            self.mq_client.subscribe(*self.subscription_routing_keys())
        except KeyboardInterrupt:
            return


    # ----------------------------------------------------------------------------------------------------------------

    def handle(self, message: Message):
        self.logger.info(f'handle - message:{JSONify.as_jdict(message)}')

        try:
            new_conf = Clock.construct_from_jdict(message.body)
        except TypeError as ex:
            self.logger.error(f'ex:{ex}')
            return

        if new_conf == Clock.load(Host):
            return

        new_conf.save(Host)

        broadcast = Message(self.publication_routing_key(), message.body)
        self.logger.info(f'handle - broadcast:{broadcast}')
        self.mq_client.publish(broadcast)
