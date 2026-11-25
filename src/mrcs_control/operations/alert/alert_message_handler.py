"""
Created on 15 Nov 2026

@author: Bruno Beloff (bbeloff@me.com)

A service that manages alert messages

Test with:
mrcs_control_publisher -v -r ALR.*.1 -m '{"type": "Alert", "id": null, "severity": "HIGH", "impact": "GLOBAL", \
"subject": "TRACK", "text": "short happened", "raised": "2026-11-15T08:43:56.970+00:00", "resolved": null}'

mrcs_control_subscriber -v -s ALR.*.002
"""

from mrcs_control.equipment.alert.persistent_alert import PersistentAlert
from mrcs_core.equipment.alert.alert import Alert
from mrcs_core.messaging.message import Message
from mrcs_core.operations.alert.alert_action import AlertAction
from mrcs_core.operations.alert.alert_command import AlertCommand
from mrcs_core.operations.alert.alert_response import AlertResponse
from mrcs_core.operations.node_command import CommandException


# --------------------------------------------------------------------------------------------------------------------

class AlertMessageHandler(object):
    """
    a service that manages alert messages
    """


    @classmethod
    def handle_alert(cls, message: Message) -> Alert:
        body_type = message.body.get('type')

        if body_type == Alert.type_name():
            alert = PersistentAlert.construct_from_jdict(message.body)

            if alert.is_resolved:
                raise ValueError(f'already resolved: {alert}')

            id = alert.save()
            return PersistentAlert.find_by_id(id)

        raise ValueError(f'upsupported message type:{body_type}')


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def handle_command(cls, body) -> AlertResponse:
        try:
            command = AlertCommand.construct_from_jdict(body)
        except Exception as exc:
            return AlertResponse.construct_error(AlertAction.UNKNOWN, exc)

        try:
            if command.action == AlertAction.RESOLVE:
                return cls.__handle_RESOLVE(command)

            if command.action == AlertAction.RESOLVE_ALL:
                return cls.__handle_RESOLVE_ALL(command)

            if command.action == AlertAction.LIST_UNRESOLVED:
                return cls.__handle_LIST_UNRESOLVED(command)

            if command.action == AlertAction.LIST_LATEST:
                return cls.__handle_LIST_RESOLVED(command)

            if command.action == AlertAction.DELETE_RESOLVED:
                return cls.__handle_DELETE_RESOLVED(command)

        except Exception as exc:
            return AlertResponse.construct_error(command.action, exc)

        raise CommandException(f'unsupported command: {command}')


    @classmethod
    def __handle_RESOLVE(cls, command: AlertCommand) -> AlertResponse:
        id = command.kwarg('id')
        alert = PersistentAlert.find_by_id(id)

        if alert is None:
            return AlertResponse.construct_error(command.action, IndexError(id))

        alert.resolve()
        alert.save()

        return AlertResponse(command.action)


    @classmethod
    def __handle_RESOLVE_ALL(cls, command: AlertCommand) -> AlertResponse:
        alerts = PersistentAlert.find_unresolved()

        for alert in alerts:
            alert.resolve()
            alert.save()

        return AlertResponse(command.action)


    @classmethod
    def __handle_LIST_UNRESOLVED(cls, command: AlertCommand) -> AlertResponse:
        alerts = PersistentAlert.find_unresolved()

        return AlertResponse(command.action, payload=list(alerts))


    @classmethod
    def __handle_LIST_RESOLVED(cls, command: AlertCommand) -> AlertResponse:
        limit = command.kwarg('limit')
        alerts = PersistentAlert.find_latest(limit)

        return AlertResponse(command.action, payload=list(alerts))


    @classmethod
    def __handle_DELETE_RESOLVED(cls, command: AlertCommand) -> AlertResponse:
        PersistentAlert.delete_resolved()

        return AlertResponse(command.action)
