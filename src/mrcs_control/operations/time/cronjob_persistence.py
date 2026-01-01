"""
Created on 1 Jan 2026

@author: Bruno Beloff (bbeloff@me.com)

SQLite database management for cron jobs

https://stackoverflow.com/questions/2701877/sqlite-table-constraint-unique-on-multiple-columns
"""

from abc import ABC

from mrcs_control.data.persistence import PersistentObject
from mrcs_control.db.dbclient import DBClient

from mrcs_core.data.iso_datetime import ISODatetime


# --------------------------------------------------------------------------------------------------------------------

class CronjobPersistence(PersistentObject, ABC):
    """
    SQLite database management for cron jobs
    """

    __DATABASE = 'Cron'

    __TABLE_NAME = 'cronjobs'
    __TABLE_VERSION = 1

    @classmethod
    def table(cls):
        return f'{cls.__TABLE_NAME}_v{cls.__TABLE_VERSION}'


    @classmethod
    def recreate_tables(cls):
        client = DBClient.instance(cls.__DATABASE)

        client.begin()
        cls.__drop_tables(client)
        cls.__create_tables(client)
        client.commit()


    @classmethod
    def create_tables(cls):
        client = DBClient.instance(cls.__DATABASE)

        cls.__create_tables(client)
        client.commit()


    @classmethod
    def drop_tables(cls):
        client = DBClient.instance(cls.__DATABASE)

        cls.__drop_tables(client)
        client.commit()


    @classmethod
    def __create_tables(cls, client):
        table = cls.table()

        sql = f'''
            CREATE TABLE IF NOT EXISTS {table} (
            id INTEGER PRIMARY KEY, 
            source TEXT NOT NULL, 
            event_id TEXT NOT NULL, 
            on_datetime TIMESTAMP,
            UNIQUE(source, event_id, on_datetime) ON CONFLICT REPLACE)
            '''
        client.execute(sql)

        sql = f'CREATE INDEX IF NOT EXISTS {table}_on_datetime ON {table}(on_datetime)'
        client.execute(sql)


    @classmethod
    def __drop_tables(cls, client):
        table = cls.table()

        sql = f'DROP INDEX IF EXISTS {table}_on_datetime'
        client.execute(sql)

        sql = f'DROP TABLE IF EXISTS {table}'
        client.execute(sql)


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def find_all(cls):
        client = DBClient.instance(cls.__DATABASE)
        table = cls.table()

        sql = f'SELECT id, source, event_id, on_datetime FROM {table} ORDER BY on_datetime, source'
        client.execute(sql)
        rows = client.fetchall()

        return (cls.construct_from_db(*fields) for fields in rows)


    @classmethod
    def find_next(cls):
        client = DBClient.instance(cls.__DATABASE)
        table = cls.table()

        sql = (f'SELECT id, source, event_id, on_datetime '
               f'FROM {table} WHERE on_datetime <= ? ORDER BY on_datetime LIMIT 1')
        client.execute(sql, data=(ISODatetime.now().dbformat(), ))
        row = client.fetchone()

        return cls.construct_from_db(*row) if row else None


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def insert(cls, job: PersistentObject):
        client = DBClient.instance(cls.__DATABASE)
        table = cls.table()

        client.begin()
        sql = f'INSERT INTO {table} (source, event_id, on_datetime) VALUES (?, ?, ?)'
        client.execute(sql, data=job.as_db_insert())
        client.commit()

        sql = 'SELECT last_insert_rowid()'
        client.execute(sql)
        client.commit()

        row = client.fetchone()

        return int(row[0])


    @classmethod
    def update(cls, entry: PersistentObject):
        raise NotImplementedError('cron jobs are immutable')


    @classmethod
    def delete(cls, id: int):
        client = DBClient.instance(cls.__DATABASE)
        table = cls.table()

        try:
            client.begin()
            sql = f'DELETE FROM {table} WHERE id = ?'
            client.execute(sql, data=(id, ))

        finally:
            client.commit()
