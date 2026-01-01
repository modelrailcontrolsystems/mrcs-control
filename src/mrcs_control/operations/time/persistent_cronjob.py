"""
Created on 1 Jan 2026

@author: Bruno Beloff (bbeloff@me.com)

represents a cron job to be performed

{
    "id": 1,
    "source": "SCH.*.001",
    "event_id": "abc",
    "on": "2026-01-01T12:17:42.919+00:00"
}
"""

from collections import OrderedDict

from mrcs_control.data.persistence import PersistentObject
from mrcs_control.operations.time.cronjob_persistence import CronjobPersistence

from mrcs_core.data.equipment_identity import EquipmentIdentifier
from mrcs_core.data.iso_datetime import ISODatetime
from mrcs_core.operations.time.cronjob import Cronjob


# --------------------------------------------------------------------------------------------------------------------

class PersistentCronjob(Cronjob, CronjobPersistence, PersistentObject):
    """
    represents a cron job to be performed
    """

    @classmethod
    def construct_from_db(cls, id, source, event_id, db_on_datetime):
        source = EquipmentIdentifier.construct_from_jdict(source)
        on_datetime = ISODatetime.construct_from_db(db_on_datetime)

        return cls(id, source, event_id, on_datetime)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, id: int | None, source: EquipmentIdentifier, event_id: str, on_datetime: ISODatetime):
        super().__init__(source, event_id, on_datetime)

        self.__id = id


    # ----------------------------------------------------------------------------------------------------------------

    def save(self):
        if self.id is not None:
            raise ValueError('cron jobs are immutable')

        return super().insert(self)


    # ----------------------------------------------------------------------------------------------------------------

    def as_db_insert(self):
        return self.source.as_json(), self.event_id, self.on_datetime.dbformat()


    def as_db_update(self):
        raise NotImplementedError('cron jobs are immutable')


    # ----------------------------------------------------------------------------------------------------------------

    def as_json(self, **kwargs):
        jdict = OrderedDict()

        jdict['id'] = self.id
        jdict['source'] = self.source
        jdict['event_id'] = self.event_id
        jdict['on'] = self.on_datetime

        return jdict


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def id(self):
        return self.__id


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'PersistentCronjob:{{id:{self.id}, source:{self.source}, event_id:{self.event_id}, '
                f'on_datetime:{self.on_datetime}}}')
