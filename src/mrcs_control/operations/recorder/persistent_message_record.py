"""
Created on 19 Dec 2025

@author: Bruno Beloff (bbeloff@me.com)

A structured representation of a message

{
    "routing": "TST.001.002.MPU.001.100",
    "body": "hello"
}

https://www.geeksforgeeks.org/python/python-sqlite-working-with-date-and-datetime/
https://stackoverflow.com/questions/17574784/sqlite-current-timestamp-with-milliseconds
https://forum.xojo.com/t/sqlite-return-id-of-record-inserted/37896/3
"""

import json

from mrcs_control.data.persistence import PersistentObject
from mrcs_control.operations.recorder.message_persistence import MessagePersistence
from mrcs_core.data.equipment_identity import EquipmentIdentifier, EquipmentFilter

from mrcs_core.data.iso_datetime import ISODatetime
from mrcs_core.operations.recorder.message_record import MessageRecord
from mrcs_core.messaging.routing_key import RoutingKey, PublicationRoutingKey


# --------------------------------------------------------------------------------------------------------------------

class PersistentMessageRecord(MessageRecord, MessagePersistence, PersistentObject):
    """
    classdocs
    """

    @classmethod
    def construct_from_db(cls, uid_field, rec_field, origin_field, source_field, target_field, body_field):
        uid = int(uid_field)
        rec = ISODatetime.construct_from_db(rec_field)

        source = EquipmentIdentifier.construct_from_jdict(source_field)
        target = EquipmentFilter.construct_from_jdict(target_field)
        routing_key = PublicationRoutingKey(source, target)

        body = json.loads(body_field)

        return cls(uid, rec, routing_key, body, origin_field)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, uid: int, rec: ISODatetime, routing_key: RoutingKey, body, origin):
        super().__init__(uid, rec, routing_key, body, origin)


    # ----------------------------------------------------------------------------------------------------------------

    def save(self):
        raise NotImplementedError('use PersistentMessage class instead')


    # ----------------------------------------------------------------------------------------------------------------

    def as_db_insert(self):
        raise NotImplementedError('use PersistentMessage class instead')


    def as_db_update(self):
        raise NotImplementedError('messages are immutable')

