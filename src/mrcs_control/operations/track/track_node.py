"""
Created on 12 Aug 2026

@author: Bruno Beloff (bbeloff@me.com)

A service that manages track equipment

Notes:
* Because BlockVoltageReport and BlockOccupancyReport messages are received at different times, the
voltage reported in the published BlockStatus message may be incorrect. BlockStatus occupancy is the source of truth.

Test with:
mrcs_control_subscriber -v -s TRK.*.2
"""

import time
from collections.abc import Callable
from typing import List

from mrcs_control.db.db_client import DbClient
from mrcs_control.dcc.z21.command.command import Command
from mrcs_control.equipment.block.persistent_block_status import PersistentBlockStatus
from mrcs_control.equipment.track.persistent_track import PersistentTrack
from mrcs_control.equipment.turnout.persistent_turnout_status import PersistentTurnoutStatus
from mrcs_control.messaging.mq_topology import MQTopology
from mrcs_control.operations.async_messaging_node import AsyncSubscriberNode
from mrcs_control.operations.control_router.control_router_node import ControlRouterNode
from mrcs_control.operations.track.track_node_identity import TrackNodeCommand, TrackNodeSerial
from mrcs_core.data.json import JSONable
from mrcs_core.equipment.block.block_report import BlockOccupancyReport, BlockVoltageReport
from mrcs_core.equipment.block.block_status import BlockStatus
from mrcs_core.equipment.equipment_enums import CRT, EquipmentType
from mrcs_core.equipment.equipment_identity import EquipmentFilter, EquipmentIdentifier
from mrcs_core.equipment.track.track_report import TrackReport
from mrcs_core.equipment.turnout.turnout_report import TurnoutReport
from mrcs_core.layout.block.block_abstract import BlockAbstract
from mrcs_core.layout.segment.turnout_abstract import TurnoutAbstract
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import PublicationRoutingKey, SubscriptionRoutingKey
from mrcs_core.operations.node_topology import NodeTopology
from mrcs_core.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

class TrackNode(AsyncSubscriberNode):
    """
    a service that manages track equipment
    """


    @classmethod
    def id(cls):
        return EquipmentIdentifier(EquipmentType.TRK, None, TrackNodeSerial.NODE)


    @classmethod
    def broadcast_id(cls) -> EquipmentIdentifier:
        return EquipmentIdentifier(EquipmentType.TRK, None, TrackNodeSerial.BLOCK_STATUS)


    @classmethod
    def subscription_routing_keys(cls) -> list[SubscriptionRoutingKey]:
        subscriptions = [SubscriptionRoutingKey(EquipmentFilter.any(), cls.id())]

        for serial in [CRT.TRACK, CRT.TURNOUT, CRT.BLOCK]:
            router_filter = EquipmentFilter.construct(EquipmentType.CRT, None, serial)
            subscriptions.append(SubscriptionRoutingKey(router_filter, EquipmentFilter.any()))

        return subscriptions


    @classmethod
    def control_routing_key(cls):
        return PublicationRoutingKey(cls.id(), ControlRouterNode.id())


    @classmethod
    def broadcast_routing_key(cls):
        return PublicationRoutingKey(cls.broadcast_id(), EquipmentFilter.any())


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def track_state(cls) -> TrackReport:
        return PersistentTrack.load(Host)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: NodeTopology.ServiceConfiguration, on_message: Callable[JSONable] | None = None):
        super().__init__(ops, MQTopology.SINGLE_PROCESS)

        self.__on_message = on_message
        self.__message_received_timestamp = time.time()


    # ----------------------------------------------------------------------------------------------------------------

    def handle_startup(self):
        self.__publish_startup_message()
        self.logger.info('ready')


    def handle_message(self, message: Message):
        self.logger.debug(f'handle_message:{message}')

        try:
            if message.routing_key.target == self.id():
                self.__handle_command_message(message)

            else:
                self.__handle_control_router_message(message)

        except Exception as exc:
            self.logger.warning(f'handle_message:{type(exc).__name__}:{exc} on:{message}')


    def __handle_command_message(self, message: Message):
        self.logger.debug(f'handle_command_message:{message}')

        if message.body == TrackNodeCommand.FIND_ALL_TURNOUTS:
            self.__publish_find_turnouts_message(message.routing_key.source)

        else:
            self.logger.warning(f'upsupported message:{message}')


    def __handle_control_router_message(self, message: Message):
        self.logger.debug(f'handle_control_router_message:{message}')

        body_type = message.body.get('type')

        if body_type == BlockOccupancyReport.type_name():
            report = BlockOccupancyReport.construct_from_jdict(message.body)

            if report.is_empty_tail:
                return  # TODO: > 1 groups add to the occupancy, they don't replace it

            period = time.time() - self.__message_received_timestamp
            self.logger.error(f'*** time since last report:{period}')
            self.__message_received_timestamp = time.time()

            self.logger.error(f'*** report:{report}')
            existing_status = PersistentBlockStatus.find_by_address(report.address)
            self.logger.error(f'*** existing_status:{existing_status}')
            self.logger.error('-')

            status = PersistentBlockStatus.update_from_block_occupancy_report(report)
            self.__publish_update_message(status)

        elif body_type == TrackReport.type_name():
            report = PersistentTrack.construct_from_jdict(message.body)
            report.save(Host)

        elif body_type == BlockVoltageReport.type_name():
            report = BlockVoltageReport.construct_from_jdict(message.body)
            PersistentBlockStatus.update_from_voltage(report)

        elif body_type == TurnoutReport.type_name():
            report = TurnoutReport.construct_from_jdict(message.body)
            PersistentTurnoutStatus.update_from_turnout_report(report)

        else:
            self.logger.warning(f'upsupported message:{message}')

        if self.on_message:
            self.on_message(message)


    # ----------------------------------------------------------------------------------------------------------------

    def __publish_startup_message(self):
        self.logger.debug('publish_startup_message')

        message = Message(self.control_routing_key(), Command.lan_can_detector())
        self.async_loop.create_task(self.publish(message))


    def __publish_update_message(self, status: BlockStatus):
        self.logger.debug('publish_update_message')

        message = Message(self.broadcast_routing_key(), status)
        self.async_loop.create_task(self.publish(message))


    def __publish_find_turnouts_message(self, client: EquipmentIdentifier):
        self.logger.debug('publish_find_turnouts_message')

        message = Message(PublicationRoutingKey(self.id(), client), PersistentTurnoutStatus.find_all())
        self.async_loop.create_task(self.publish(message))


    # ----------------------------------------------------------------------------------------------------------------

    def populate(self, blocks: BlockAbstract, turnouts: TurnoutAbstract) -> None:
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


    def run(self, *args, **kwargs) -> None:
        self.__setup()
        super().run()


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
        on_message = self.on_message.__name__ if self.on_message else None
        routing_keys = '[' + ', '.join(map(str, self.subscription_routing_keys())) + ']'

        return (f'TrackNode:{{routing_keys:{routing_keys}, on_message:{on_message}, '
                f'ops:{self.ops}, mq_client:{self.mq_client}}}')
