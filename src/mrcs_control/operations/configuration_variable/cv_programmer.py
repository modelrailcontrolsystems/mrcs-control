"""
Created on 11 Oct 2026

@author: Bruno Beloff (bbeloff@me.com)

A CV programmer that can command CV reads and writes
"""

from mrcs_control.cli.internal.topic_subscriber_node import TopicSubscriberNode
from mrcs_control.dcc.z21.command.command import Command, XCommand
from mrcs_control.operations.configuration_variable.cv_programmer_state import CVProgrammerState
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


# --------------------------------------------------------------------------------------------------------------------

class CVProgrammer(object):
    """
    commands CV reads and writes
    """


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: NodeTopology.ServiceConfiguration, id: EquipmentIdentifier):
        self.__id = id

        control_router_filter = EquipmentFilter(EquipmentType.CRT, None, None)
        self.__subscription_routing_key = SubscriptionRoutingKey(control_router_filter, EquipmentFilter.any())

        publication_routing_key = PublicationRoutingKey(self.id, ControlRouterNode.id())
        self.__publication_routing_key = publication_routing_key

        self.__state = CVProgrammerState()

        TopicSubscriberNode.set_id(self.id)
        TopicSubscriberNode.set_subscription_routing_keys(self.subscription_routing_key)

        self.__node = TopicSubscriberNode.construct_node(ops, self.on_message)

        self.__logger = Logging.getLogger()


    # ----------------------------------------------------------------------------------------------------------------

    def read_all(self):
        self.state.go_READ(*CVAddress.items())

        initial_message = self.__cv_message(self.state.next_command())
        self.__node.run(initial_publication=initial_message, final_publication=self.__power_on_message())


    def write(self, decoder: Manufacturer | None, *cvs: CV):
        self.state.go_WRITE(decoder, *cvs)

        initial_message = self.__cv_message(self.state.next_command())
        self.__node.run(initial_publication=initial_message, final_publication=self.__power_on_message())


    def close(self):
        self.node.close()


    # ----------------------------------------------------------------------------------------------------------------

    def on_message(self, message: Message):
        try:
            cv_report = CVReport.construct_from_jdict(message.body)
            cv = CVBuilder.construct_from_report(cv_report)
            self.state.append_cv(cv)
        except TypeError:
            return

        except Exception as exc:
            self.logger.warning(exc)
            return

        try:
            message = self.__cv_message(self.state.next_command())
        except IndexError:
            self.__node.request_shutdown()

        self.node.async_loop.create_task(self.node.publish(message))


    def __cv_message(self, command: Command):
        return Message(self.publication_routing_key, command)


    def __power_on_message(self):
        return Message(self.publication_routing_key, XCommand.lan_x_set_track_power(TrackMode.COMMAND_POWER_ON))


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def id(self):
        return self.__id


    @property
    def subscription_routing_key(self):
        return self.__subscription_routing_key


    @property
    def publication_routing_key(self):
        return self.__publication_routing_key


    @property
    def state(self):
        return self.__state


    @property
    def cvs(self):
        return self.state.cvs


    @property
    def node(self):
        return self.__node


    @property
    def logger(self):
        return self.__logger


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'CVProgrammer:{{id:{self.id}, subscription_routing_key:{self.subscription_routing_key}, '
                f'publication_routing_key:{self.subscription_routing_key}, state:{self.state}}}')
