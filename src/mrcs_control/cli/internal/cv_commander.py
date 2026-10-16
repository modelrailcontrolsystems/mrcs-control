"""
Created on 11 Oct 2026

@author: Bruno Beloff (bbeloff@me.com)

Commands CV reads and writes
"""

from enum import StrEnum

from mrcs_control.cli.internal.topic_subscriber_node import TopicSubscriberNode
from mrcs_control.dcc.z21.command.command import XCommand
from mrcs_control.operations.control_router.control_router_node import ControlRouterNode
from mrcs_core.data.equipment_identity import EquipmentFilter, EquipmentIdentifier, EquipmentType
from mrcs_core.equipment.conviguration_variable.cv_report import CVReport
from mrcs_core.equipment.track.track_enums import TrackMode
from mrcs_core.equipment.track.track_report import TrackReport
from mrcs_core.inventory.configuration_variable.cv import CV
from mrcs_core.inventory.configuration_variable.cv_address import CVAddress
from mrcs_core.inventory.configuration_variable.cv_builder import CVBuilder
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import PublicationRoutingKey, SubscriptionRoutingKey
from mrcs_core.operations.node_topology import NodeTopology
from mrcs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

class Mode(StrEnum):
    STANDBY = 'STANDBY'
    READ = 'READ'
    WRITE = 'WRITE'
    POWER = 'POWER'


# --------------------------------------------------------------------------------------------------------------------

class CVCommander(object):
    """
    Commands CV reads and writes
    """


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: NodeTopology.ServiceConfiguration, id: EquipmentIdentifier):
        self.__id = id

        self.__publication_routing_key = PublicationRoutingKey(self.id, ControlRouterNode.id())

        control_router_filter = EquipmentFilter(EquipmentType.CRT, None, None)  # TODO: tidy everywhere!
        self.__subscription_routing_key = SubscriptionRoutingKey(control_router_filter, EquipmentFilter.any())

        TopicSubscriberNode.set_id(self.id)
        TopicSubscriberNode.set_subscription_routing_keys(self.subscription_routing_key)

        self.__node = TopicSubscriberNode.construct_node(ops, self.on_message)

        self.__mode = Mode.STANDBY
        self.__cv_queue = []
        self.__cvs = []

        self.__logger = Logging.getLogger()


    # ----------------------------------------------------------------------------------------------------------------

    def read_all(self):
        self.__cv_queue = list(CVAddress.items())
        self.__cvs = []

        self.__node.run(initial_publication=self.__next_read_message())


    def write(self, *cvs: CV):
        self.__cv_queue = list(cvs)
        self.__cvs = []

        self.__node.run(initial_publication=self.__next_write_message())


    def close(self):
        self.node.close()


    # ----------------------------------------------------------------------------------------------------------------

    def on_message(self, message: Message):
        if self.mode in (Mode.READ, Mode.WRITE):
            self.__on_cv_message(message)
            return

        if self.mode == Mode.POWER:
            self.__on_power_message(message)
            return


    def __on_cv_message(self, message: Message):
        try:
            cv_report = CVReport.construct_from_jdict(message.body)
            cv = CVBuilder.construct_from_report(cv_report)
            self.__logger.info(cv)

            self.cvs.append(cv)
        except TypeError:
            return

        try:
            message = self.__next_write_message() if self.mode == Mode.WRITE else self.__next_read_message()
        except IndexError:
            message = self.__power_message()

        self.node.async_loop.create_task(self.node.publish(message))


    def __on_power_message(self, message: Message):
        try:
            track_report = TrackReport.construct_from_jdict(message.body)
            if track_report.mode == TrackMode.POWER_ON:
                self.__mode = Mode.STANDBY
                self.__node.request_shutdown()
        except TypeError:
            return


    def __next_read_message(self):
        self.__mode = Mode.READ
        cv_address = self.cv_queue.pop(0)  # may raise IndexError
        return Message(self.publication_routing_key, XCommand.lan_x_get_cv(cv_address.value))


    def __next_write_message(self):
        self.__mode = Mode.WRITE
        while True:
            cv = self.cv_queue.pop(0)  # may raise IndexError
            if cv.is_writeable():
                break
        return Message(self.publication_routing_key, XCommand.lan_x_set_cv(cv.cv_address.value, cv.value))


    def __power_message(self):
        self.__mode = Mode.POWER
        return Message(self.publication_routing_key, XCommand.lan_x_set_track_power(TrackMode.COMMAND_POWER_ON))


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def id(self):
        return self.__id


    @property
    def publication_routing_key(self):
        return self.__publication_routing_key


    @property
    def subscription_routing_key(self):
        return self.__subscription_routing_key


    @property
    def mode(self):
        return self.__mode


    @property
    def cv_queue(self):
        return self.__cv_queue


    @property
    def cvs(self):
        return self.__cvs


    @property
    def node(self):
        return self.__node


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'CVCommander:{{id:{self.id}, publication_routing_key:{self.publication_routing_key}, '
                f'subscription_routing_key:{self.subscription_routing_key}, mode:{self.mode}, '
                f'cv_queue:{self.cv_queue}, cvs:{self.cvs}}}')
