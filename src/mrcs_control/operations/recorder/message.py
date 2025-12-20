"""
Created on 2 Nov 2025

@author: Bruno Beloff (bbeloff@me.com)

A structured representation of a message

{
    "routing": "TST.001.002.MPU.001.100",
    "body": "hello"
}
"""

from mrcs_control.data.persistence import PersistentObject
from mrcs_control.operations.recorder.message_persistence import MessagePersistence

from mrcs_core.data.json import JSONify
from mrcs_core.messaging.message import Message
from mrcs_core.messaging.routing_key import RoutingKey


# --------------------------------------------------------------------------------------------------------------------

class PersistentMessage(Message, MessagePersistence, PersistentObject):
    """
    classdocs message.routing_key, message.body
    """

    @classmethod
    def widen(cls, message: Message):
        return cls(*message.__dict__.values())


    @classmethod
    def construct_from_db(cls, *fields):
        raise NotImplementedError('use PersistentMessageRecord class instead')


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, routing_key: RoutingKey, body):
        super().__init__(routing_key, body)


    # ----------------------------------------------------------------------------------------------------------------

    def save(self):
        return super().insert(self)


    # ----------------------------------------------------------------------------------------------------------------

    def as_db_insert(self):
        return self.routing_key.as_json(), JSONify.dumps(self.body)


    def as_db_update(self):
        raise NotImplementedError('messages are immutable')
