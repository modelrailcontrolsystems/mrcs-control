"""
Created on 17 Jan 2026

@author: Bruno Beloff (bbeloff@me.com)

A SubscriberNode that provides the authority for clock configuration
This is a single point in the system where the clock configuration is persisted and - when changed -
the change is broadcasted.
"""

from mrcs_control.operations.messaging_node import SubscriberNode
from mrcs_control.operations.operation_mode import OperationService
from mrcs_control.operations.time.cron import CRN

from mrcs_core.data.equipment_identity import EquipmentIdentifier, EquipmentType, EquipmentFilter
from mrcs_core.data.json import JSONify
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import SubscriptionRoutingKey, PublicationRoutingKey
from mrcs_core.operations.time.clock import Clock
from mrcs_core.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

class ClockManagerNode(SubscriberNode):
    """
    an authority for clock configuration
    """


    @classmethod
    def id(cls):
        return EquipmentIdentifier(EquipmentType.CRN, None, CRN.ClockManager)


    @classmethod
    def subscription_routing_keys(cls):
        return (SubscriptionRoutingKey(EquipmentFilter.any(), cls.id()),)


    @classmethod
    def publication_routing_key(cls):
        return PublicationRoutingKey(cls.id(), EquipmentFilter.any())


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: OperationService):
        super().__init__(ops)


    # ----------------------------------------------------------------------------------------------------------------

    def handle_message(self, incoming: Message):
        self.logger.info(f'handle_message - incoming:{JSONify.as_jdict(incoming)}')

        try:
            clock = Clock.construct_from_jdict(incoming.body)
        except Exception:
            self.logger.warning(f'invalid message body:{incoming.body}')
            return

        if clock == Clock.load(Host):
            return

        clock.save(Host)

        outgoing = Message(self.publication_routing_key(), incoming.body, origin=incoming.origin)
        self.logger.info(f'handle - outgoing:{JSONify.as_jdict(outgoing)}')
        self.mq_client.publish(outgoing)


    # ----------------------------------------------------------------------------------------------------------------

    def subscribe(self):
        self.mq_client.connect()

        try:
            self.mq_client.subscribe(*self.subscription_routing_keys())
        except KeyboardInterrupt:
            return
