"""
Created on 17 Jan 2026

@author: Bruno Beloff (bbeloff@me.com)

A SubscriberNode that provides the authority for clock configuration
This is a single point in the system where the clock configuration is persisted and - when changed -
the change is broadcasted.
"""

from mrcs_control.messaging.mq_enums import MQTopology
from mrcs_control.operations.messaging_node import SubscriberNode
from mrcs_control.operations.node_enums import NodeTopology
from mrcs_control.operations.time.cron import CRN
from mrcs_core.data.equipment_identity import EquipmentFilter, EquipmentIdentifier, EquipmentType
from mrcs_core.data.json import JSONify
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import PublicationRoutingKey, SubscriptionRoutingKey
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
    def publication_routing_key(cls):
        return PublicationRoutingKey(cls.id(), EquipmentFilter.any())


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: NodeTopology.ServiceConfiguration):
        super().__init__(ops, MQTopology.SINGLE, self.id())


    # ----------------------------------------------------------------------------------------------------------------

    def subscription_routing_keys(self):
        return (SubscriptionRoutingKey(EquipmentFilter.any(), self.id()),)


    def handle_message(self, message: Message):
        self.logger.debug(f'handle_message - incoming:{JSONify.as_jdict(message)}')

        try:
            clock = Clock.construct_from_jdict(message.body)
        except Exception:
            self.logger.warning(f'invalid message body:{message.body}')
            return

        if clock == Clock.load(Host):
            return

        clock.save(Host)

        outgoing = Message(self.publication_routing_key(), message.body, origin=message.origin)
        self.mq_client.publish(outgoing)


    # ----------------------------------------------------------------------------------------------------------------

    def subscribe(self):
        self.mq_client.connect()

        try:
            self.mq_client.subscribe(*self.subscription_routing_keys())
        except KeyboardInterrupt:
            return
