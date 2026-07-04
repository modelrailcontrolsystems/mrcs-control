"""
Created on 14 Nov 2025

@author: Bruno Beloff (bbeloff@me.com)

An interface that must be implemented by business objects that can be persisted using an RDBMS.
Required to prevent circular imports between business objects and persistence helper classes.
"""

from abc import ABC, abstractmethod
from typing import List

from mrcs_control.db.db_client import DbClient
from mrcs_control.db.db_name import DbName


# --------------------------------------------------------------------------------------------------------------------

class PersistenceManager(ABC):
    """
    classdocs
    """


    @classmethod
    def recreate_tables(cls):
        client = DbClient.instance(cls.db_name())

        try:
            client.txEXCLUSIVE()
            cls._drop_tables(client)
            cls._create_tables(client)
            client.txCOMMIT()

        except Exception as ex:
            client.txROLLBACK(ex)


    @classmethod
    def create_tables(cls):
        client = DbClient.instance(cls.db_name())

        try:
            client.txEXCLUSIVE()
            cls._create_tables(client)
            client.txCOMMIT()

        except Exception as ex:
            client.txROLLBACK(ex)


    @classmethod
    def drop_tables(cls):
        client = DbClient.instance(cls.db_name())

        try:
            client.txEXCLUSIVE()
            cls._drop_tables(client)
            client.txCOMMIT()

        except Exception as ex:
            client.txROLLBACK(ex)


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    @abstractmethod
    def db_name(cls) -> DbName:
        pass


    @classmethod
    @abstractmethod
    def _create_tables(cls, client: DbClient):
        pass


    @classmethod
    @abstractmethod
    def _drop_tables(cls, client: DbClient):
        pass


    # ----------------------------------------------------------------------------------------------------------------


    @classmethod
    @abstractmethod
    def insert(cls, entry: PersistentObject):
        pass


    @classmethod
    @abstractmethod
    def update(cls, entry: PersistentObject):
        pass


# --------------------------------------------------------------------------------------------------------------------

class PersistentObject(PersistenceManager, ABC):
    """
    classdocs
    """


    @classmethod
    @abstractmethod
    def construct_from_db(cls, *fields):
        pass


    @abstractmethod
    def save(self):
        pass


    @abstractmethod
    def as_db_insert(self):
        pass


    @abstractmethod
    def as_db_update(self):
        pass


    # ----------------------------------------------------------------------------------------------------------------

    def children(self) -> List[PersistentObject]:
        return []
