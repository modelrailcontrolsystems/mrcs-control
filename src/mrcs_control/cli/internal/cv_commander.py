"""
Created on 11 Oct 2026

@author: Bruno Beloff (bbeloff@me.com)

Commands CV reads and writes
"""

from enum import StrEnum

from mrcs_control.cli.internal.topic_subscriber_node import TopicSubscriberNode
from mrcs_control.dcc.z21.command.command import XCommand
from mrcs_control.operations.control_router.control_router_node import ControlRouterNode
from mrcs_core.equipment.conviguration_variable.cv_report import CVReport
from mrcs_core.equipment.equipment_enums import EquipmentType
from mrcs_core.equipment.equipment_identity import EquipmentFilter, EquipmentIdentifier
from mrcs_core.equipment.track.track_enums import TrackMode
from mrcs_core.inventory.configuration_variable.cv import CV
from mrcs_core.inventory.configuration_variable.cv_address import CVAddress
from mrcs_core.inventory.configuration_variable.cv_builder import CVBuilder
from mrcs_core.inventory.motive_power_unit.manufacturer import Manufacturer
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import PublicationRoutingKey, SubscriptionRoutingKey
from mrcs_core.operations.node_topology import NodeTopology
from mrcs_core.sys.logging import Logging


# TODO: create a State object for this, like SpeedTrialRunner / SpeedTrialState
# TODO: move to contol/operations/configuration_variable/cv_programmer
# --------------------------------------------------------------------------------------------------------------------

class Mode(StrEnum):
    STANDBY = 'STANDBY'
    READ = 'READ'
    WRITE = 'WRITE'


# --------------------------------------------------------------------------------------------------------------------

class CVCommander(object):
    """
    Commands CV reads and writes
    """


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: NodeTopology.ServiceConfiguration, id: EquipmentIdentifier):
        self.__id = id

        self.__publication_routing_key = PublicationRoutingKey(self.id, ControlRouterNode.id())

        control_router_filter = EquipmentFilter(EquipmentType.CRT, None, None)
        self.__subscription_routing_key = SubscriptionRoutingKey(control_router_filter, EquipmentFilter.any())

        TopicSubscriberNode.set_id(self.id)
        TopicSubscriberNode.set_subscription_routing_keys(self.subscription_routing_key)

        self.__node = TopicSubscriberNode.construct_node(ops, self.on_message)

        self.__mode = Mode.STANDBY
        self.__decoder = None
        self.__cv_queue = []
        self.__cvs = []

        self.__logger = Logging.getLogger()


    # ----------------------------------------------------------------------------------------------------------------

    def read_all(self):
        self.__cv_queue = list(CVAddress.items())
        self.__cvs = []

        self.__node.run(initial_publication=self.__next_read_message(), final_publication=self.__power_on_message())


    def write(self, decoder: Manufacturer | None, *cvs: CV):
        self.__decoder = decoder
        self.__cv_queue = list(cvs)
        self.__cvs = []

        self.__node.run(initial_publication=self.__next_write_message(), final_publication=self.__power_on_message())


    def close(self):
        self.node.close()


    # ----------------------------------------------------------------------------------------------------------------

    def on_message(self, message: Message):
        try:
            cv_report = CVReport.construct_from_jdict(message.body)
            cv = CVBuilder.construct_from_report(cv_report)
            self.logger.info(cv)

            self.cvs.append(cv)
        except TypeError:
            return

        except Exception as exc:
            self.logger.warning(exc)
            return

        try:
            message = self.__next_write_message() if self.mode == Mode.WRITE else self.__next_read_message()
        except IndexError:
            self.__node.request_shutdown()

        self.node.async_loop.create_task(self.node.publish(message))


    def __next_read_message(self):
        self.__mode = Mode.READ
        cv_address = self.cv_queue.pop(0)  # may raise IndexError

        return Message(self.publication_routing_key, XCommand.lan_x_get_cv(cv_address.value))


    def __next_write_message(self):
        self.__mode = Mode.WRITE
        while True:
            cv = self.cv_queue.pop(0)  # may raise IndexError
            if cv.is_writeable(self.decoder):
                break

        return Message(self.publication_routing_key, XCommand.lan_x_set_cv(cv.cv_address.value, cv.value))


    def __power_on_message(self):
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
    def decoder(self):
        return self.__decoder


    @property
    def cv_queue(self):
        return self.__cv_queue


    @property
    def cvs(self):
        return self.__cvs


    @property
    def node(self):
        return self.__node


    @property
    def logger(self):
        return self.__logger


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'CVCommander:{{id:{self.id}, publication_routing_key:{self.publication_routing_key}, '
                f'subscription_routing_key:{self.subscription_routing_key}, mode:{self.mode}, '
                f'cv_queue:{self.cv_queue}, cvs:{self.cvs}}}')
