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

from mrcs_control.operations.recorder.message_persistence import MessagePersistence

from mrcs_core.data.iso_datetime import ISODatetime
from mrcs_core.operations.recorder.message_record import MessageRecord
from mrcs_core.messaging.routing_key import RoutingKey, PublicationRoutingKey


# --------------------------------------------------------------------------------------------------------------------

class PersistentMessageRecord(MessageRecord, MessagePersistence):
    """
    classdocs
    """

    # TODO: construct from superclass

    @classmethod
    def construct_from_db(cls, uid_field, rec_field, routing_key_field, body_field):
        uid = int(uid_field)
        rec = ISODatetime.construct_from_db(rec_field)
        routing_key = PublicationRoutingKey.construct_from_db(routing_key_field)
        body = json.loads(body_field)

        return cls(uid, rec, routing_key, body)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, uid: int, rec: ISODatetime, routing_key: RoutingKey, body):
        super().__init__(uid, rec, routing_key, body)


    # ----------------------------------------------------------------------------------------------------------------

    def save(self):
        raise NotImplementedError('use PersistentMessage class instead')


    # ----------------------------------------------------------------------------------------------------------------

    def as_db_insert(self):
        raise NotImplementedError('use PersistentMessage class instead')


    def as_db_update(self):
        raise NotImplementedError('messages are immutable')

