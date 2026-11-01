"""
Created on 31 Oct 2026

@author: Bruno Beloff (bbeloff@me.com)

A service that runs MPU speed trials
"""

import time

from mrcs_control.dcc.z21.command.command import XCommand
from mrcs_control.operations.control_router.control_router_node import ControlRouterNode
from mrcs_control.operations.route.route_planner import RoutePlanner
from mrcs_control.operations.speed.speed_node import SpeedNode
from mrcs_core.equipment.block.block_enums import BlockHeading
from mrcs_core.equipment.block.block_status import BlockStatus
from mrcs_core.equipment.motive_power_unit.mpu_enums import MPUDirection
from mrcs_core.equipment.motive_power_unit.mpu_status import MPUStatus
from mrcs_core.inventory.motive_power_unit.mpu import MPU
from mrcs_core.layout.block.block import Block
from mrcs_core.layout.layout import Layout
from mrcs_core.layout.segment.segment_location import SegmentLocation
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import PublicationRoutingKey
from mrcs_core.operations.node_topology import NodeTopology
from mrcs_core.operations.speed.speed_log import SpeedLog
from mrcs_core.operations.speed.speed_run import SpeedRun
from mrcs_core.operations.speed.speed_trial import SpeedTrial
from mrcs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

class SpeedTrialRunner(object):
    """
    a service that runs MPU speed trials
    """


    @classmethod
    def publication_routing_key(cls):
        return PublicationRoutingKey(SpeedNode.id(), ControlRouterNode.id())


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: NodeTopology.ServiceConfiguration, layout: Layout, speed_trial: SpeedTrial,
                 mpu: MPU, block: Block):
        self.__layout = layout
        self.__speed_trial = speed_trial
        self.__mpu = mpu
        self.__block = block

        self.__set_speed = 0
        self.__latest_reported_speed = 0
        self.__speed_log = None

        self.__planner = RoutePlanner(layout.as_prolog_segments(), layout.as_prolog_links())
        self.__planner.initialise()

        self.__node = SpeedNode(ops, on_message=self.on_message)
        self.__logger = Logging.getLogger()


    # ----------------------------------------------------------------------------------------------------------------

    def on_message(self, message):
        body_type = message.body.get('type')

        if body_type == MPUStatus.type_name():
            self.__on_mpu_message(MPUStatus.construct_from_jdict(message.body))

        if body_type == BlockStatus.type_name():
            self.__on_block_message(BlockStatus.construct_from_jdict(message.body))


    def __on_mpu_message(self, mpu_status: MPUStatus):
        self.__latest_reported_speed = mpu_status.speed

        if self.speed_log:
            self.speed_log.mark(self.latest_reported_speed)


    def __on_block_message(self, block_status: BlockStatus):
        if not block_status.contains_mpu(self.mpu.address):
            return

        if self.speed_log:
            if block_status.label != self.block.label:
                self.logger.info('trial end')
                self.speed_log.mark(self.latest_reported_speed)

                time.sleep(self.speed_log.elapsed_time / 2)
                self.node.request_shutdown()

        else:
            if block_status.label == self.block.label:
                self.logger.info(f'trial start - set speed: {self.set_speed}')
                self.__speed_log = SpeedLog.start(self.latest_reported_speed)


    # ----------------------------------------------------------------------------------------------------------------

    def run(self, set_speed: int):
        self.__reset(set_speed)

        heading = self.__heading()
        length = self.__trial_block_length()

        go_message = self.__mpu_message(self.publication_routing_key(), heading, set_speed)
        stop_message = self.__mpu_message(self.publication_routing_key(), heading, 0)

        self.node.drain()
        self.node.run(initial_publication=go_message, final_publication=stop_message)

        if self.speed_log:
            run = SpeedRun.construct(length, heading, set_speed, self.speed_log)
            self.speed_trial.add_run(run)


    def __heading(self) -> BlockHeading:
        initial_block = self.__initial_block()

        start_location = SegmentLocation(initial_block.label, initial_block.segments[0].label)
        block_location = SegmentLocation(self.block.label, self.block.segments[0].label)

        route = self.planner.shortest_route(start_location, block_location)
        if route is None:
            raise RuntimeError(f'The heading {start_location.dot_path} - {block_location.dot_path} is not available.')

        return route.direction


    def __trial_block_length(self) -> BlockHeading:
        start_location = SegmentLocation(self.block.label, self.block.segments[0].label)
        end_location = SegmentLocation(self.block.label, self.block.segments[-1].label)

        route = self.planner.shortest_route(start_location, end_location)
        if route is None:
            raise RuntimeError(f'The length {start_location.dot_path} - {end_location.dot_path} is not available.')

        return route.length


    def __initial_block(self) -> Block:
        initial_block_status = BlockStatus.containing_block(self.node.find_all_blocks(), self.mpu.address)
        if initial_block_status is None:
            raise RuntimeError(f'The MPU {self.mpu.label} cannot be found on the layout.')

        return self.layout.block(initial_block_status.label)


    def __mpu_message(self, publication_routing_key: PublicationRoutingKey, heading: BlockHeading, speed: int):
        direction = MPUDirection.FORWARD if heading == BlockHeading.UP else MPUDirection.REVERSE  # TODO: fix direction
        drive_command = XCommand.lan_x_set_mpu_drive(self.mpu.address, direction, speed)

        return Message(publication_routing_key, drive_command)


    def __reset(self, set_speed: int):
        self.__set_speed = set_speed
        self.__latest_reported_speed = 0
        self.__speed_log = None


    # ----------------------------------------------------------------------------------------------------------------

    def close(self):
        self.logger.info('SpeedTrialRunner - close')
        self.node.request_shutdown()
        self.node.close()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def mpu(self):
        return self.__mpu


    @property
    def block(self):
        return self.__block


    # ----------------------------------------------------------------------------------------------------------------


    @property
    def set_speed(self):
        return self.__set_speed


    @property
    def latest_reported_speed(self):
        return self.__latest_reported_speed


    @property
    def speed_trial(self):
        return self.__speed_trial


    @property
    def speed_log(self):
        return self.__speed_log


    # ----------------------------------------------------------------------------------------------------------------


    @property
    def layout(self):
        return self.__layout


    @property
    def planner(self):
        return self.__planner


    @property
    def node(self):
        return self.__node


    @property
    def logger(self):
        return self.__logger


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'SpeedTrialRunner:{{mpu:{self.mpu.label}, block:{self.block.label}}}'
