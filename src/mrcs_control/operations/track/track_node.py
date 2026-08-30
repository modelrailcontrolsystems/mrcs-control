"""
Created on 12 Aug 2026

@author: Bruno Beloff (bbeloff@me.com)

A service that manages track equipment
"""

from collections.abc import Callable
from typing import List

from mrcs_control.cli.inventory.block_inventory import BlockInventory
from mrcs_control.cli.inventory.turnout_inventory import TurnoutInventory
from mrcs_control.db.db_client import DbClient
from mrcs_control.dcc.z21.command.command import Command
from mrcs_control.equipment.block.persistent_block_status import PersistentBlockStatus
from mrcs_control.equipment.track.persistent_track import PersistentTrack
from mrcs_control.equipment.turnout.persistent_turnout_status import PersistentTurnoutStatus
from mrcs_control.messaging.mq_topology import MQTopology
from mrcs_control.operations.async_messaging_node import AsyncSubscriberNode
from mrcs_control.operations.control_router.control_router_identity import ControlRouterSerial
from mrcs_control.operations.control_router.control_router_node import ControlRouterNode
from mrcs_control.operations.node_topology import NodeTopology
from mrcs_core.data.equipment_identity import EquipmentFilter, EquipmentIdentifier, EquipmentType
from mrcs_core.data.json import JSONable
from mrcs_core.equipment.block.block_report import BlockOccupancyReport, BlockVoltageReport
from mrcs_core.equipment.track.track_report import TrackReport
from mrcs_core.equipment.turnout.turnout_report import TurnoutReport
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import PublicationRoutingKey, SubscriptionRoutingKey
from mrcs_core.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

class TrackNode(AsyncSubscriberNode):
    """
    a service that manages track equipment
    """


    @classmethod
    def id(cls):
        return EquipmentIdentifier(EquipmentType.TRN, None, 1)


    @classmethod
    def subscription_routing_keys(cls):
        router_source = EquipmentFilter.construct(EquipmentType.CRT, None, ControlRouterSerial.Track)

        return (SubscriptionRoutingKey(EquipmentFilter.any(), cls.id()),
                SubscriptionRoutingKey(router_source, EquipmentFilter.any()))


    @classmethod
    def track_state(cls) -> TrackReport:
        return PersistentTrack.load(Host)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: NodeTopology.ServiceConfiguration, on_message: Callable[JSONable] | None = None):
        super().__init__(ops, MQTopology.SINGLE_PROCESS)

        self.__on_message = on_message


    # ----------------------------------------------------------------------------------------------------------------

    def handle_startup(self):
        self.logger.debug('handle_startup')
        self.async_loop.create_task(self.publish_message())


    async def publish_message(self):
        self.logger.debug('publish_message')

        routing_key = PublicationRoutingKey(self.id(), ControlRouterNode.id())
        message = Message(routing_key, Command.lan_can_detector())
        self.async_loop.create_task(self.publish(message))


    def handle_message(self, message: Message):
        self.logger.debug(f'handle_message:{message}')

        if message.routing_key.target == self.id():
            self.logger.info(f'received command:{message.body}')
            # TODO: act on commands
            return

        body_type = message.body.get('type')

        # TODO: keep a count / timing of occupancy reports for each block -
        # TODO: subsequent reports within a time period are handled differently

        if body_type == BlockOccupancyReport.__name__:
            report = BlockOccupancyReport.construct_from_jdict(message.body)
            PersistentBlockStatus.update_from_block_occupancy_report(report)

        if body_type == TrackReport.__name__:
            report = PersistentTrack.construct_from_jdict(message.body)
            report.save(Host)

        if body_type == BlockVoltageReport.__name__:
            report = BlockVoltageReport.construct_from_jdict(message.body)
            PersistentBlockStatus.update_from_voltage(report)

        if body_type == TurnoutReport.__name__:
            report = TurnoutReport.construct_from_jdict(message.body)
            PersistentTurnoutStatus.update_from_turnout_report(report)

        if self.on_message:
            self.on_message(message)


    # ----------------------------------------------------------------------------------------------------------------

    def populate(self, blocks: BlockInventory, turnouts: TurnoutInventory) -> None:
        DbClient.set_client_db_mode(self.ops.db_mode)
        PersistentBlockStatus.recreate_tables()
        PersistentTurnoutStatus.recreate_tables()

        for block in blocks.items:
            PersistentBlockStatus.narrow(block).save()

        for turnout in turnouts.items:
            PersistentTurnoutStatus.narrow(turnout).save()


    def find_all_blocks(self) -> List[PersistentBlockStatus]:
        self.__setup()
        return PersistentBlockStatus.find_all()


    def find_all_turnouts(self) -> List[PersistentTurnoutStatus]:
        self.__setup()
        return PersistentTurnoutStatus.find_all()


    def __setup(self):
        DbClient.set_client_db_mode(self.ops.db_mode)
        PersistentBlockStatus.create_tables()
        PersistentTurnoutStatus.create_tables()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def on_message(self):
        return self.__on_message


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        on_message = self.on_message.__name__
        routing_keys = '[' + ', '.join([str(key) for key in self.subscription_routing_keys()]) + ']'

        return (f'TrackNode:{{routing_keys:{routing_keys}, on_message:{on_message}, '
                f'ops:{self.ops}, mq_client:{self.mq_client}}}')
