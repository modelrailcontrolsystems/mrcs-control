"""
Created on 16 Nov 2025

@author: Bruno Beloff (bbeloff@me.com)

A gathering-together of service operation modes

https://stackoverflow.com/questions/37678418/python-enums-with-complex-types
"""

from enum import unique, Enum

from mrcs_control.db.dbclient import DBMode
from mrcs_control.messaging.mqclient import MQMode

from mrcs_core.data.meta_enum import MetaEnum


# --------------------------------------------------------------------------------------------------------------------

class OperationService(object):
    """
    A gathering-together of service operation modes
    """

    def __init__(self, id: str, db_mode: DBMode, mq_mode: MQMode):
        self.__id = id
        self.__db_mode = db_mode
        self.__mq_mode = mq_mode


    # ----------------------------------------------------------------------------------------------------------------

    def broker_filter(self, items):
        return [item for item in items if item.name.startswith(self.mq_mode)]


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def id(self):
        return self.__id


    @property
    def db_mode(self):
        return self.__db_mode


    @property
    def mq_mode(self):
        return self.__mq_mode


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return f'OperationService:{{id:{self.id}, db_mode:{self.db_mode}, mq_mode:{self.mq_mode}}}'


# --------------------------------------------------------------------------------------------------------------------

@unique
class OperationMode(Enum, metaclass=MetaEnum):
    """
    An enumeration of all the possible operation modes
    """

    TEST = OperationService('TEST', DBMode.TEST, MQMode.TEST)
    LIVE = OperationService('LIVE', DBMode.LIVE, MQMode.LIVE)
