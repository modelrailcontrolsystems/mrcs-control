"""
Created on 17 Jan 2026

@author: Bruno Beloff (bbeloff@me.com)

A SubscriberNode that provides the authority for clock configuration
This is a single point in the system where the clock configuration is persisted and - when changed -
the change is broadcasted.
"""

from mrcs_control.messaging.mq_topology import MQTopology
from mrcs_control.operations.messaging_node import SubscriberNode
from mrcs_control.operations.node_topology import NodeTopology
from mrcs_control.operations.time.cron_serial import CronSerial
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
        return EquipmentIdentifier(EquipmentType.CLK, None, CronSerial.CLOCK_MANAGER)


    @classmethod
    def publication_routing_key(cls):
        return PublicationRoutingKey(cls.id(), EquipmentFilter.any())


    @classmethod
    def subscription_routing_keys(cls) -> list[SubscriptionRoutingKey]:
        return [SubscriptionRoutingKey(EquipmentFilter.any(), cls.id())]


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: NodeTopology.ServiceConfiguration):
        super().__init__(ops, MQTopology.SINGLE_PROCESS)


    # ----------------------------------------------------------------------------------------------------------------

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
        if not self.mq_client.is_connected:
            self.mq_client.connect()

        try:
            self.mq_client.subscribe(*self.subscription_routing_keys())
        except KeyboardInterrupt:
            return
