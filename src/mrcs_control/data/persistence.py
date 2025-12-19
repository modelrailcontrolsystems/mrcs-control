"""
Created on 14 Nov 2025

@author: Bruno Beloff (bbeloff@me.com)

An interface that must be implemented by business objects that can be persisted using an RDBMS.
Required to prevent circular imports between business objects and persistence helper classes.
"""

from abc import ABC, abstractmethod


# --------------------------------------------------------------------------------------------------------------------

class PersistenceManager(ABC):
    """
    classdocs
    """

    @classmethod
    @abstractmethod
    def create_tables(cls):
        pass


    @classmethod
    @abstractmethod
    def drop_tables(cls):
        pass


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
