"""
Created on 9 Nov 2025

@author: Bruno Beloff (bbeloff@me.com)

An SQLite database client, guaranteeing one connection per database, per process

https://www.sqlitetutorial.net/sqlite-python/
https://forum.xojo.com/t/sqlite-return-id-of-record-inserted/37896
https://iafisher.com/blog/2021/10/using-sqlite-effectively-in-python

use BEGIN / COMMIT throughout?
https://iafisher.com/blog/2021/10/using-sqlite-effectively-in-python
"""

import os
import sqlite3

from enum import unique, StrEnum
from sqlite3 import ProgrammingError

from mrcs_core.data.meta_enum import MetaEnum
from mrcs_core.sys.host import Host
from mrcs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

@unique
class DBMode(StrEnum, metaclass=MetaEnum):
    """
    An enumeration of all the possible database modes
    """

    TEST = 'test'         # test
    LIVE = 'live'         # production


# --------------------------------------------------------------------------------------------------------------------

class DBClient(object):
    """
    An SQLite database client
    """

    __client_db_mode = DBMode.LIVE

    @classmethod
    def client_db_mode(cls):
        return cls.__client_db_mode


    @classmethod
    def set_client_db_mode(cls, db_mode: DBMode):
        if cls.__client_db_mode == db_mode:
            return

        if cls.__clients:
            raise RuntimeError('client_db_mode cannot be set while there are existing clients')

        cls.__client_db_mode = db_mode


    # ----------------------------------------------------------------------------------------------------------------

    __clients = {}

    @classmethod
    def instance(cls, db_name) -> DBClient:
        if db_name not in cls.__clients:
            cls.__clients[db_name] = DBClient(cls.__client_db_mode, db_name)
            cls.__clients[db_name].__open()

        return cls.__clients[db_name]


    @classmethod
    def kill(cls, db_name):
        if db_name in list(cls.__clients):
            try:
                cls.__clients[db_name].__close()
            except ProgrammingError:
                # being dropped by another thread?
                pass

            del cls.__clients[db_name]


    @classmethod
    def kill_all(cls):
        for db_name in list(cls.__clients):
            cls.kill(db_name)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, db_mode, db_name):
        self.__db_mode = db_mode
        self.__db_name = db_name

        self.__connection = None
        self.__cursor = None
        self.__logger = Logging.getLogger()


    # ----------------------------------------------------------------------------------------------------------------

    def execute(self, statement, data=None):
        if self.connection is None:
            raise RuntimeError('execute: no connection')

        if self.cursor is None:
            raise RuntimeError('execute: no cursor')

        if data:
            self.cursor.execute(statement, data)
        else:
            self.cursor.execute(statement)


    def begin(self):
        pass


    def commit(self):
        self.connection.commit()


    def fetchall(self):
        return self.cursor.fetchall()


    def fetchone(self):
        return self.cursor.fetchone()


    def __open(self):
        filename = '.'.join([self.db_name, 'db'])

        os.makedirs(Host.mrcs_db_abs_dir(self.db_mode), exist_ok=True)
        self.__connection = sqlite3.connect(Host.mrcs_db_abs_file(self.db_mode, filename))
        self.__cursor = self.connection.cursor()


    def __close(self):
        if self.connection:
            self.connection.close()
            self.__cursor = None
            self.__connection = None


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def db_mode(self):
        return self.__db_mode


    @property
    def db_name(self):
        return self.__db_name


    @property
    def connection(self):
        return self.__connection


    @property
    def cursor(self):
        return self.__cursor


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return (f'DBClient:{{db_mode:{self.db_mode}, db_name:{self.db_name}, '
                f'connection:{self.connection}, cursor:{self.cursor}}}')
