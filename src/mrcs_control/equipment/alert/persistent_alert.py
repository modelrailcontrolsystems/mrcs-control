"""
Created on 15 Nov 2026

@author: Bruno Beloff (bbeloff@me.com)

A structured representation of an alert.

Note that all fields are imutable, with the execption of:
* id - may transition from None to an int
* resolved_at - may transition from None to an ISODatetime

{
    "type": "Alert",
    "id": 1,
    "severity": "HIGH",
    "impact": "GLOBAL",
    "subject": "TRACK",
    "text": "short happened",
    "raised": "2026-11-15T08:43:56.970+00:00",
    "resolved": "2026-11-15T11:09:05.573+00:00"
}
"""

from typing import Self

from mrcs_control.data.persistence import PersistentObject
from mrcs_control.equipment.alert.alert_persistence import AlertPersistence
from mrcs_core.data.iso_datetime import ISODatetime
from mrcs_core.equipment.alert.alert import Alert
from mrcs_core.equipment.alert.alert_enums import Impact, Severity, Subject


# --------------------------------------------------------------------------------------------------------------------

class PersistentAlert(Alert, AlertPersistence, PersistentObject):
    """
    classdocs message.routing_key, message.body
    """


    @classmethod
    def type_name(cls) -> str:
        return Alert.type_name()  # Persistent classes are for internal use only - advertise the base class


    @classmethod
    def narrow(cls, alert: Alert) -> Self:
        return cls(alert.id, alert.severity, alert.impact, alert.subject, alert.text, alert.raised_at,
                   alert.resolved_at)


    @classmethod
    def construct_from_db(cls, row, *child_rows) -> Self:
        id, db_severity, db_impact, db_subject, text, db_raised_at, db_resolved_at = row

        severity = Severity[db_severity]  # may raise KeyError
        impact = Impact(db_impact)
        subject = Subject(db_subject)

        raised_at = ISODatetime.construct_from_db_field(db_raised_at)
        resolved_at = ISODatetime.construct_from_db_field(db_resolved_at)

        return cls(id, severity, impact, subject, text, raised_at, resolved_at)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, id: int | None, severity: Severity, impact: Impact, subject: Subject, text: str,
                 raised_at: ISODatetime, resolved_at: ISODatetime | None):
        super().__init__(id, severity, impact, subject, text, raised_at, resolved_at)


    # ----------------------------------------------------------------------------------------------------------------

    def save(self) -> int:
        if self.has_id:
            type(self).update_resolved(self)
            return self.id

        return type(self).insert(self)


    # ----------------------------------------------------------------------------------------------------------------

    def as_db_insert(self):
        db_raised_at = self.raised_at.dbformat()
        db_resolved_at = None if self.resolved_at is None else self.resolved_at.dbformat()

        return self.severity.name, self.impact, self.subject, self.text, db_raised_at, db_resolved_at


    def as_db_update(self):
        db_resolved_at = None if self.resolved_at is None else self.resolved_at.dbformat()

        return db_resolved_at, self.id
