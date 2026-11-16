"""
Created on 15 Nov 2026

@author: Bruno Beloff (bbeloff@me.com)

An ACK / NACK in response to a ResolutionCommand

{
    "type": "ResolutionResponse",
    "alert_id": 1,
    "error": "RuntimeError: there was a problem"
}
"""

from collections import OrderedDict
from typing import Any, Self

from mrcs_core.data.json import JSONable


# --------------------------------------------------------------------------------------------------------------------

class ResolutionResponse(JSONable):
    """
    an ACK / NACK in response to a ResolutionCommand
    """


    @classmethod
    def construct_from_jdict(cls, jdict) -> Self:
        type_name = jdict.get('type')

        if type_name != cls.type_name():
            raise TypeError(f'required type:{cls.type_name()} got:{type_name}')

        alert_id = int(jdict.get('alert_id'))
        error = jdict.get('error')

        return cls(alert_id, error=error)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, alert_id: int, error: str | None = None):
        self.__alert_id = alert_id
        self.__error = error


    def __eq__(self, other: Any) -> bool:
        try:
            return self.alert_id == other.alert_id and self.error == other.error
        except (AttributeError, TypeError):
            return False


    # ----------------------------------------------------------------------------------------------------------------

    def is_ACK(self):
        return self.error is None


    def is_NACK(self):
        return self.error is not None


    # ----------------------------------------------------------------------------------------------------------------

    def as_json(self, **kwargs):
        jdict = OrderedDict()

        jdict['type'] = self.type_name()

        jdict['alert_id'] = self.alert_id

        if self.error is not None:
            jdict['error'] = self.error

        return jdict


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def alert_id(self):
        return self.__alert_id


    @property
    def error(self):
        return self.__error


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'ResolutionResponse:{{alert_id:{self.alert_id}, error:{self.error}}}'
