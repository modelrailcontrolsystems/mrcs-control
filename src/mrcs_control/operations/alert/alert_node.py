"""
Created on 15 Nov 2026

@author: Bruno Beloff (bbeloff@me.com)

A service that manages alert messages

Test with:
mrcs_control_publisher -v -r ALR.*.1 -m '{"type": "Alert", "id": null, "severity": "HIGH", "impact": "GLOBAL", \
"subject": "TRACK", "text": "short happened", "raised": "2026-11-15T08:43:56.970+00:00", "resolved": null}'

mrcs_control_subscriber -v -s ALR.*.002
"""

from collections.abc import Callable

from mrcs_control.db.db_client import DbClient
from mrcs_control.equipment.alert.persistent_alert import PersistentAlert
from mrcs_control.messaging.mq_topology import MQTopology
from mrcs_control.operations.alert.alert_node_identity import AlertNodeSerial
from mrcs_control.operations.async_messaging_node import AsyncSubscriberNode
from mrcs_core.data.json import JSONable
from mrcs_core.equipment.alert.alert import Alert
from mrcs_core.equipment.equipment_enums import EquipmentType
from mrcs_core.equipment.equipment_identity import EquipmentFilter, EquipmentIdentifier
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import PublicationRoutingKey, SubscriptionRoutingKey
from mrcs_core.operations.node_topology import NodeTopology


# --------------------------------------------------------------------------------------------------------------------

class AlertNode(AsyncSubscriberNode):
    """
    a service that manages alert messages
    """


    # TODO: a good pattern for ids - re-examine the other nodes


    @classmethod
    def id(cls) -> EquipmentIdentifier:
        return EquipmentIdentifier(EquipmentType.ALR, None, AlertNodeSerial.NODE)


    @classmethod
    def broadcast_id(cls) -> EquipmentIdentifier:
        return EquipmentIdentifier(EquipmentType.ALR, None, AlertNodeSerial.UNRESOLVED)


    @classmethod
    def resolution_id(cls) -> EquipmentIdentifier:
        return EquipmentIdentifier(EquipmentType.ALR, None, AlertNodeSerial.RESOLUTION)


    @classmethod
    def subscription_routing_keys(cls) -> list[SubscriptionRoutingKey]:
        return [
            SubscriptionRoutingKey(EquipmentFilter.any(), cls.id()),
            SubscriptionRoutingKey(EquipmentFilter.any(), cls.resolution_id())
        ]


    @classmethod
    def broadcast_routing_key(cls):
        return PublicationRoutingKey(cls.broadcast_id(), EquipmentFilter.any())


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, ops: NodeTopology.ServiceConfiguration, on_message: Callable[JSONable] | None = None):
        super().__init__(ops, MQTopology.SINGLE_PROCESS)

        self.__on_message = on_message


    # ----------------------------------------------------------------------------------------------------------------

    def handle_startup(self):
        self.__publish_startup_messages()
        self.logger.info('ready')


    def handle_message(self, message: Message):
        self.logger.debug(f'handle_message:{message.routing_key}')

        try:
            if message.routing_key.target == self.resolution_id():
                self.__handle_resolution_command(message.body)
                return

            if message.routing_key.target == self.id():
                self.__handle_unprocessed_message(message.body)
                if self.on_message:
                    self.on_message(message)

        except Exception as exc:
            self.logger.warning(f'handle_message:{type(exc).__name__}:{exc} on:{message}')


    def __handle_resolution_command(self, body):
        # TODO: handle resolution commands
        return


    def __handle_unprocessed_message(self, body):
        body_type = body.get('type')

        if body_type == Alert.type_name():
            alert = PersistentAlert.construct_from_jdict(body)
            id = alert.save()

            if not alert.is_resolved:
                self.__publish_unresolved_message(PersistentAlert.find_by_id(id))

            return

        self.logger.warning(f'upsupported message type:{body_type}')


    # ----------------------------------------------------------------------------------------------------------------

    def __publish_startup_messages(self):
        self.logger.debug('publish_startup_messages')

        for alert in PersistentAlert.find_unresolved():
            self.__publish_unresolved_message(alert)


    def __publish_unresolved_message(self, alert: Alert):
        self.logger.debug('publish_unresolved_message')

        message = Message(self.broadcast_routing_key(), alert)
        self.async_loop.create_task(self.publish(message))


    def __publish_resolution_message(self, alert: Alert):
        pass


    # ----------------------------------------------------------------------------------------------------------------

    def clear(self) -> None:
        DbClient.set_client_db_mode(self.ops.db_mode)
        PersistentAlert.recreate_tables()


    def list_unresolved(self) -> list[Alert]:
        DbClient.set_client_db_mode(self.ops.db_mode)
        return list(PersistentAlert.find_unresolved())


    def list_all(self, limit: int) -> list[Alert]:
        DbClient.set_client_db_mode(self.ops.db_mode)
        return list(PersistentAlert.find_latest(limit))


    def run(self, *args, **kwargs) -> None:
        self.__setup()
        super().run()


    def __setup(self):
        DbClient.set_client_db_mode(self.ops.db_mode)
        PersistentAlert.create_tables()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def on_message(self):
        return self.__on_message


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        on_message = None if self.on_message is None else self.on_message.__name__
        routing_keys = '[' + ', '.join(map(str, self.subscription_routing_keys())) + ']'

        return (f'AlertNode:{{routing_keys:{routing_keys}, on_message:{on_message}, '
                f'ops:{self.ops}, mq_client:{self.mq_client}}}')
