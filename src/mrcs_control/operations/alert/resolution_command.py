"""
Created on 15 Nov 2026

@author: Bruno Beloff (bbeloff@me.com)

A command to the AlertNode to mark an Alert as resolved

{
    "type": "ResolutionCommand",
    "alert_id": 1,
    "requires_response": true
}
"""

from collections import OrderedDict
from typing import Any, Self

from mrcs_core.data.json import JSONable


# --------------------------------------------------------------------------------------------------------------------

class ResolutionCommand(JSONable):
    """
    a command to the AlertNode to mark an Alert as resolved
    """


    @classmethod
    def construct_from_jdict(cls, jdict) -> Self:
        type_name = jdict.get('type')

        if type_name != cls.type_name():
            raise TypeError(f'required type:{cls.type_name()} got:{type_name}')

        alert_id = int(jdict.get('alert_id'))
        requires_response = bool(jdict.get('requires_response'))

        return cls(alert_id, requires_response)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, alert_id: int, requires_response: bool):
        self.__alert_id = alert_id
        self.__requires_response = requires_response


    def __eq__(self, other: Any) -> bool:
        try:
            return self.alert_id == other.alert_id and self.requires_response == other.requires_response
        except (AttributeError, TypeError):
            return False


    # ----------------------------------------------------------------------------------------------------------------

    def as_json(self, **kwargs):
        jdict = OrderedDict()

        jdict['type'] = self.type_name()

        jdict['alert_id'] = self.alert_id
        jdict['requires_response'] = self.requires_response

        return jdict


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def alert_id(self):
        return self.__alert_id


    @property
    def requires_response(self):
        return self.__requires_response


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'ResolutionCommand:{{alert_id:{self.alert_id}, requires_response:{self.requires_response}}}'
