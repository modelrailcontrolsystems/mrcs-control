"""
Created on 12 Aug 2026

@author: Bruno Beloff (bbeloff@me.com)

A service that manages turnouts
"""

from typing import List

from mypy.nodes import Callable

from mrcs_control.db.db_client import DbClient
from mrcs_control.equipment.control_router.control_router_identity import ControlRouterSerial
from mrcs_control.equipment.turnout.persistent_turnout_status import PersistentTurnoutStatus
from mrcs_control.messaging.mq_topology import MQTopology
from mrcs_control.operations.messaging_node import SubscriberNode
from mrcs_control.operations.node_topology import NodeTopology
from mrcs_core.data.equipment_identity import EquipmentFilter, EquipmentIdentifier, EquipmentType
from mrcs_core.data.json import JSONable
from mrcs_core.equipment.turnout.turnout_report import TurnoutReport
from mrcs_core.equipment.turnout.turnout_status import TurnoutStatus
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import SubscriptionRoutingKey


# --------------------------------------------------------------------------------------------------------------------

class TurnoutNode(SubscriberNode):
    """
    a service that manages turnouts
    """


    @classmethod
    def id(cls):
        return EquipmentIdentifier(EquipmentType.TRN, None, 1)


    @classmethod
    def subscription_routing_keys(cls):
        router_source = EquipmentFilter.construct(EquipmentType.CRT, None, ControlRouterSerial.Track)

        return (SubscriptionRoutingKey(EquipmentFilter.any(), cls.id()),
                SubscriptionRoutingKey(router_source, EquipmentFilter.any()))


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: NodeTopology.ServiceConfiguration, on_message: Callable[JSONable] | None = None):
        super().__init__(ops, MQTopology.SINGLE)

        self.__on_message = on_message


    # ----------------------------------------------------------------------------------------------------------------

    def handle_message(self, message: Message):
        self.logger.debug(f'handle_message:{message}')

        if message.routing_key.target == self.id():
            self.logger.info(f'received command:{message.body}')
            return

        try:
            report = TurnoutReport.construct_from_jdict(message.body)
        except TypeError:
            self.logger.error(f'failed to construct TurnoutReport from message body:{message.body}')
            return

        try:
            message = PersistentTurnoutStatus.update_from_turnout_report(report)
        except Exception as exc:
            self.logger.error(f'failed to update PersistentTurnoutStatus from TurnoutReport:{exc}')
            return

        if self.on_message:
            self.on_message(message)


    # ----------------------------------------------------------------------------------------------------------------

    def populate(self, turnouts: List[TurnoutStatus]) -> List[PersistentTurnoutStatus]:
        DbClient.set_client_db_mode(self.ops.db_mode)
        PersistentTurnoutStatus.recreate_tables()

        for turnout in turnouts:
            PersistentTurnoutStatus.narrow(turnout).save()

        return PersistentTurnoutStatus.find_all()


    def find_all(self) -> List[PersistentTurnoutStatus]:
        DbClient.set_client_db_mode(self.ops.db_mode)
        PersistentTurnoutStatus.create_tables()

        return PersistentTurnoutStatus.find_all()


    def subscribe(self) -> None:
        DbClient.set_client_db_mode(self.ops.db_mode)
        PersistentTurnoutStatus.create_tables()

        self.mq_client.connect()
        self.logger.info('subscribed')

        try:
            self.mq_client.subscribe(*self.subscription_routing_keys())
        except KeyboardInterrupt:
            return


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def on_message(self):
        return self.__on_message


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        on_message = self.on_message.__name__
        routing_keys = '[' + ', '.join([str(key) for key in self.subscription_routing_keys()]) + ']'

        return (f'TurnoutNode:{{routing_keys:{routing_keys}, on_message:{on_message}, '
                f'ops:{self.ops}, mq_client:{self.mq_client}}}')
