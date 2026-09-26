"""
Created on 26 Sep 2026

@author: Bruno Beloff (bbeloff@me.com)

A one-shot turnout configuration finder
"""

from mrcs_control.cli.internal.topic_subscriber_node import TopicSubscriberNode
from mrcs_control.operations.track.track_node import TrackNode
from mrcs_control.operations.track.track_node_identity import TrackNodeCommand
from mrcs_core.data.equipment_identity import EquipmentIdentifier
from mrcs_core.equipment.turnout.turnout_configuration import TurnoutConfiguration
from mrcs_core.equipment.turnout.turnout_status import TurnoutStatus
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import PublicationRoutingKey
from mrcs_core.operations.node_topology import NodeTopology


# --------------------------------------------------------------------------------------------------------------------

class TurnoutConfigurationFinder(object):
    """
    a one-shot turnout configuration finder
    """


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, id: EquipmentIdentifier):
        self.__id = id

        self.__node = None
        self.__turnouts = []


    # ----------------------------------------------------------------------------------------------------------------

    def find(self, ops: NodeTopology.ServiceConfiguration):
        publication_routing_key = PublicationRoutingKey(self.id, TrackNode.id())
        subscription_routing_key = publication_routing_key.reversed()

        TopicSubscriberNode.set_id(self.id)
        TopicSubscriberNode.set_subscription_routing_keys([subscription_routing_key])

        self.__node = TopicSubscriberNode.construct_node(ops, self.on_message)

        # start subscriber...
        command_message = Message(publication_routing_key, TrackNodeCommand.FIND_ALL_TURNOUTS)
        self.__node.run(initial_publication=command_message)

        # subscriber has stopped...
        return TurnoutConfiguration.construct_from_turnouts(*self.turnouts)


    def on_message(self, message):
        self.__turnouts = [TurnoutStatus.construct_from_jdict(jdict) for jdict in message.body]
        self.__node.request_shutdown()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def id(self):
        return self.__id


    @property
    def turnouts(self):
        return self.__turnouts


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'TurnoutConfigurationFinder:{{id:{self.id}, turnouts:{self.turnouts}}}'
