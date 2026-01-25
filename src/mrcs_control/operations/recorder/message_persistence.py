"""
Created on 9 Nov 2025

@author: Bruno Beloff (bbeloff@me.com)

SQLite database management for messages

https://forum.xojo.com/t/sqlite-return-id-of-record-inserted/37896/3
"""

from abc import ABC

from mrcs_control.data.persistence import PersistentObject
from mrcs_control.db.db_client import DbClient
from mrcs_control.db.db_name import DbName


# --------------------------------------------------------------------------------------------------------------------

class MessagePersistence(PersistentObject, ABC):
    """
    SQLite database management for messages
    """

    __DATABASE = DbName.MessageLog

    __TABLE_NAME = 'messages'
    __TABLE_VERSION = 1

    @classmethod
    def table(cls):
        return f'{cls.__TABLE_NAME}_v{cls.__TABLE_VERSION}'


    @classmethod
    def recreate_tables(cls):
        client = DbClient.instance(cls.__DATABASE)

        client.begin()
        cls.__drop_tables(client)
        cls.__create_tables(client)
        client.commit()


    @classmethod
    def create_tables(cls):
        client = DbClient.instance(cls.__DATABASE)

        cls.__create_tables(client)
        client.commit()


    @classmethod
    def drop_tables(cls):
        client = DbClient.instance(cls.__DATABASE)

        cls.__drop_tables(client)
        client.commit()


    @classmethod
    def __create_tables(cls, client):
        table = cls.table()

        sql = f'''
            CREATE TABLE IF NOT EXISTS {table} (
            id INTEGER PRIMARY KEY, 
            rec TIMESTAMP NOT NULL DEFAULT(datetime('subsec')), 
            origin TEXT NOT NULL, 
            source TEXT NOT NULL, 
            target TEXT NOT NULL, 
            body TEXT NOT NULL 
        )'''
        client.execute(sql)

        sql = f'CREATE INDEX IF NOT EXISTS {table}_id ON {table}(id)'
        client.execute(sql)

        sql = f'CREATE INDEX IF NOT EXISTS {table}_rec ON {table}(rec)'
        client.execute(sql)

        sql = f'CREATE INDEX IF NOT EXISTS {table}_origin ON {table}(origin)'
        client.execute(sql)

        sql = f'CREATE INDEX IF NOT EXISTS {table}_source ON {table}(source)'
        client.execute(sql)

        sql = f'CREATE INDEX IF NOT EXISTS {table}_target ON {table}(target)'
        client.execute(sql)


    @classmethod
    def __drop_tables(cls, client):
        table = cls.table()

        sql = f'DROP INDEX IF EXISTS {table}_id'
        client.execute(sql)

        sql = f'DROP INDEX IF EXISTS {table}_rec'
        client.execute(sql)

        sql = f'DROP INDEX IF EXISTS {table}_origin'
        client.execute(sql)

        sql = f'DROP INDEX IF EXISTS {table}_source'
        client.execute(sql)

        sql = f'DROP INDEX IF EXISTS {table}_target'
        client.execute(sql)

        sql = f'DROP TABLE IF EXISTS {table}'
        client.execute(sql)


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def find_latest(cls, limit: int):
        client = DbClient.instance(cls.__DATABASE)
        table = cls.table()

        sql = f'SELECT * FROM {table} WHERE id IN (SELECT id FROM {table} ORDER BY id DESC LIMIT {limit})'
        client.execute(sql)

        rows = client.fetchall()

        return (cls.construct_from_db(*fields) for fields in rows)


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def insert(cls, entry: PersistentObject):
        client = DbClient.instance(cls.__DATABASE)
        table = cls.table()

        client.begin()
        sql = f'INSERT INTO {table} (origin, source, target, body) VALUES (?, ?, ?, ?)'
        client.execute(sql, data=entry.as_db_insert())

        sql = 'SELECT last_insert_rowid()'
        client.execute(sql)
        client.commit()

        row = client.fetchone()

        return int(row[0])


    @classmethod
    def test_insert(cls, rec, entry: PersistentObject):
        client = DbClient.instance(cls.__DATABASE)
        table = cls.table()

        client.begin()
        sql = f'INSERT INTO {table} (rec, origin, source, target, body) VALUES (?, ?, ?, ?, ?)'
        client.execute(sql, data=(rec,) + entry.as_db_insert())

        sql = 'SELECT last_insert_rowid()'
        client.execute(sql)
        client.commit()

        row = client.fetchone()

        return int(row[0])


    @classmethod
    def update(cls, entry: PersistentObject):
        raise NotImplementedError('messages are immutable')
