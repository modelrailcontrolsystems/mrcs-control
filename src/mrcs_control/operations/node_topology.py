"""
Created on 16 Nov 2025

@author: Bruno Beloff (bbeloff@me.com)

A gathering-together of service operation modes

https://stackoverflow.com/questions/37678418/python-enums-with-complex-types
"""

from enum import Enum, unique

from mrcs_control.db.db_client import DbMode
from mrcs_control.messaging.mq_topology import MQMode
from mrcs_core.data.meta_enum import MetaEnum


# --------------------------------------------------------------------------------------------------------------------

@unique
class NodeTopology(Enum, metaclass=MetaEnum):
    """
    An enumeration of all the possible operation modes
    """


    # ----------------------------------------------------------------------------------------------------------------


    class ServiceConfiguration(object):
        """
        A gathering-together of service operation modes
        """


        # ------------------------------------------------------------------------------------------------------------


        def __init__(self, id: str, db_mode: DbMode, mq_mode: MQMode):
            self.__id = id
            self.__db_mode = db_mode
            self.__mq_mode = mq_mode


        # ------------------------------------------------------------------------------------------------------------

        def broker_filter(self, items):
            return [item for item in items if item.name.startswith(self.mq_mode)]


        # ------------------------------------------------------------------------------------------------------------

        @property
        def id(self):
            return self.__id


        @property
        def db_mode(self):
            return self.__db_mode


        @property
        def mq_mode(self):
            return self.__mq_mode


        # ------------------------------------------------------------------------------------------------------------

        def __str__(self, *args, **kwargs):
            return f'NodeTopology.ServiceConfiguration:{{id:{self.id}, db_mode:{self.db_mode}, mq_mode:{self.mq_mode}}}'


    # ----------------------------------------------------------------------------------------------------------------

    TEST = ServiceConfiguration('TEST', DbMode.TEST, MQMode.TEST)
    LIVE = ServiceConfiguration('LIVE', DbMode.LIVE, MQMode.LIVE)
