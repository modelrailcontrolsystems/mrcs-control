"""
Created on 31 Oct 2026

@author: Bruno Beloff (bbeloff@me.com)

A service that runs MPU speed trials
"""

import time

from mrcs_control.dcc.z21.command.command import XCommand
from mrcs_control.operations.route.route_planner import RoutePlanner
from mrcs_control.operations.speed.speed_trial_node import SpeedTrialNode
from mrcs_control.operations.speed.speed_trial_state import SpeedTrialState
from mrcs_core.equipment.block.block_enums import BlockHeading
from mrcs_core.equipment.block.block_status import BlockStatus
from mrcs_core.equipment.motive_power_unit.mpu_enums import MPUDirection
from mrcs_core.equipment.motive_power_unit.mpu_status import MPUStatus
from mrcs_core.inventory.motive_power_unit.mpu import MPU
from mrcs_core.layout.block.block import Block
from mrcs_core.layout.layout import Layout
from mrcs_core.layout.route import Route
from mrcs_core.layout.segment.segment_location import SegmentLocation
from mrcs_core.messaging.message import Message
from mrcs_core.operations.node_topology import NodeTopology
from mrcs_core.operations.speed.speed_run import SpeedRun
from mrcs_core.operations.speed.speed_trial import SpeedTrial
from mrcs_core.operations.speed.speed_trial_exception import SpeedTrialException
from mrcs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

class SpeedTrialRunner(object):
    """
    a service that runs MPU speed trials
    """

    RUNOFF_AFTER_ENDED = 0.5  # proportion of the trial running time after ENDED and before STOPPING


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: NodeTopology.ServiceConfiguration, layout: Layout, speed_trial: SpeedTrial,
                 mpu: MPU, trial_block: Block):
        self.__layout = layout
        self.__speed_trial = speed_trial
        self.__mpu = mpu
        self.__trial_block = trial_block
        self.__journey_block_labels: list[str] = []

        self.__state = SpeedTrialState()

        self.__planner = RoutePlanner(layout.as_prolog_segments(), layout.as_prolog_links())
        self.__planner.initialise()

        self.__node = SpeedTrialNode(ops, on_message=self.on_message)
        self.__logger = Logging.getLogger()


    # ----------------------------------------------------------------------------------------------------------------

    async def on_message(self, message) -> None:
        body_type = message.body.get('type')

        if body_type == MPUStatus.type_name():
            await self.__on_mpu_message(MPUStatus.construct_from_jdict(message.body))

        if body_type == BlockStatus.type_name():
            await self.__on_block_message(BlockStatus.construct_from_jdict(message.body))


    async def __on_mpu_message(self, mpu_status: MPUStatus) -> None:
        self.state.latest_reported_speed = mpu_status.reported_speed

        if self.state.is_TRIAL_RUNNING():
            self.state.mark()

        elif self.state.is_STOPPING() and mpu_status.reported_speed == 0:
            self.state.go_STOPPED()
            self.node.request_shutdown()


    async def __on_block_message(self, block_status: BlockStatus) -> None:
        if not block_status.contains_mpu(self.mpu.address):
            return

        if self.state.is_STARTING():
            if block_status.label == self.trial_block.label:
                self.state.go_TRIAL_RUNNING()

        elif self.state.is_TRIAL_RUNNING():
            if block_status.label not in self.journey_block_labels:
                self.state.go_TRIAL_ENDED()

                time.sleep(self.state.speed_log.elapsed_time * self.RUNOFF_AFTER_ENDED)
                stop_message = self.__mpu_message(self.state.heading, 0)
                await self.node.publish_message(stop_message)
                self.state.go_STOPPING()


    def __mpu_message(self, heading: BlockHeading, speed: int) -> Message:
        direction = MPUDirection.FORWARD if heading == BlockHeading.UP else MPUDirection.REVERSE
        # TODO: fix direction using occupancy
        drive_command = XCommand.lan_x_set_mpu_drive(self.mpu.address, direction, speed)

        return Message(self.node.control_routing_key(), drive_command)


    # ----------------------------------------------------------------------------------------------------------------

    def run(self, set_speed: int) -> None:
        route = self.__route()
        length = self.__trial_block_length()

        self.__journey_block_labels = route.block_labels()

        go_message = self.__mpu_message(route.direction, set_speed)
        stop_message = self.__mpu_message(route.direction, 0)

        self.logger.info(f'running for speed {set_speed} heading {route.direction.name}')
        self.state.go_STARTING(route.direction)

        self.node.drain()
        self.node.run(initial_publication=go_message, final_publication=stop_message)

        if self.state.is_STOPPED():
            run = SpeedRun.construct(self.mpu.scale, length, route.direction, set_speed, self.state.speed_log)
            self.speed_trial.add_run(run)


    def __route(self, ) -> Route:
        current_block = self.__current_block()

        start = SegmentLocation(current_block.label, current_block.segments[0].label)
        trial_block = SegmentLocation(self.trial_block.label, self.trial_block.segments[0].label)

        route = self.planner.shortest_route(start, trial_block)
        if route is None:
            raise SpeedTrialException(f'The heading {start.dot_path} - {trial_block.dot_path} is not available.')

        return route


    def __current_block(self) -> Block:
        current_block_status = BlockStatus.containing_block(self.node.find_all_blocks(), self.mpu.address)

        if current_block_status is None:
            raise SpeedTrialException(f'The MPU {self.mpu.label} cannot be found on the layout.')

        if current_block_status.label == self.trial_block.label:
            raise SpeedTrialException(f'The MPU is currently in the trial block - move it out before starting the run.')

        return self.layout.block(current_block_status.label)


    def __trial_block_length(self) -> int:
        start = SegmentLocation(self.trial_block.label, self.trial_block.segments[0].label)
        end = SegmentLocation(self.trial_block.label, self.trial_block.segments[-1].label)

        route = self.planner.shortest_route(start, end)
        if route is None:
            raise SpeedTrialException(f'The length {start.dot_path} - {end.dot_path} is not available.')

        return route.length


    # ----------------------------------------------------------------------------------------------------------------

    def close(self):
        self.logger.debug('SpeedTrialRunner - close')

        self.node.request_shutdown()
        self.node.close()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def layout(self):
        return self.__layout


    @property
    def speed_trial(self):
        return self.__speed_trial


    @property
    def mpu(self):
        return self.__mpu


    @property
    def trial_block(self):
        return self.__trial_block


    @property
    def journey_block_labels(self):
        return self.__journey_block_labels


    @property
    def state(self):
        return self.__state


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
        return (f'SpeedTrialRunner:{{mpu:{self.mpu.label}, trial_block:{self.trial_block.label}, '
                f'journey_block_labels:{self.journey_block_labels}, state:{self.state}}}')
