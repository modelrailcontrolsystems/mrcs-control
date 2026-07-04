"""
Created on 1 Jan 2026

@author: Bruno Beloff (bbeloff@me.com)

SQLite database management for cron jobs
Note that the cron components work in model time, not true time.

https://stackoverflow.com/questions/2701877/sqlite-table-constraint-unique-on-multiple-columns
"""

from abc import ABC

from mrcs_control.data.persistence import PersistentObject
from mrcs_control.db.db_client import DbClient
from mrcs_control.db.db_name import DbName
from mrcs_core.data.iso_datetime import ISODatetime


# --------------------------------------------------------------------------------------------------------------------

class CronjobPersistence(PersistentObject, ABC):
    """
    SQLite database management for cron jobs
    """

    __DB_NAME = DbName.Cron

    __TABLE_NAME = 'cronjobs'
    __TABLE_VERSION = 1


    @classmethod
    def db_name(cls) -> DbName:
        return cls.__DB_NAME


    @classmethod
    def table(cls):
        return f'{cls.__TABLE_NAME}_v{cls.__TABLE_VERSION}'


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def _create_tables(cls, client):
        table = cls.table()

        sql = f'''
            CREATE TABLE IF NOT EXISTS {table} (
            id INTEGER PRIMARY KEY, 
            target TEXT NOT NULL, 
            event_id TEXT NOT NULL, 
            on_datetime TIMESTAMP,
            UNIQUE(target, event_id, on_datetime) ON CONFLICT REPLACE)
            '''
        client.execute(sql)

        sql = f'CREATE INDEX IF NOT EXISTS {table}_id ON {table}(id)'
        client.execute(sql)

        sql = f'CREATE INDEX IF NOT EXISTS {table}_on_datetime ON {table}(on_datetime)'
        client.execute(sql)

        sql = f'CREATE INDEX IF NOT EXISTS {table}_on_target ON {table}(target)'
        client.execute(sql)


    @classmethod
    def _drop_tables(cls, client):
        table = cls.table()

        sql = f'DROP INDEX IF EXISTS {table}_id'
        client.execute(sql)

        sql = f'DROP INDEX IF EXISTS {table}_on_datetime'
        client.execute(sql)

        sql = f'DROP INDEX IF EXISTS {table}_on_target'
        client.execute(sql)

        sql = f'DROP TABLE IF EXISTS {table}'
        client.execute(sql)


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def find_all(cls):
        client = DbClient.instance(cls.db_name())
        table = cls.table()

        sql = f'SELECT id, target, event_id, on_datetime FROM {table} ORDER BY on_datetime, target'
        client.execute(sql)
        rows = client.fetchall()

        return (cls.construct_from_db(*fields) for fields in rows)


    @classmethod
    def find_next(cls, now: ISODatetime):
        client = DbClient.instance(cls.db_name())
        table = cls.table()

        sql = (f'SELECT id, target, event_id, on_datetime '
               f'FROM {table} WHERE on_datetime <= ? ORDER BY on_datetime LIMIT 1')
        client.execute(sql, data=(now.dbformat(),))
        row = client.fetchone()

        return cls.construct_from_db(*row) if row else None


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def insert(cls, job: PersistentObject):
        client = DbClient.instance(cls.db_name())
        table = cls.table()

        try:
            client.txIMMEDIATE()

            sql = f'INSERT INTO {table} (target, event_id, on_datetime) VALUES (?, ?, ?)'
            client.execute(sql, data=job.as_db_insert())

            client.txCOMMIT()

            sql = 'SELECT last_insert_rowid()'
            client.execute(sql)

            row = client.fetchone()

            return int(row[0])

        except Exception as ex:
            client.txROLLBACK(ex)


    @classmethod
    def update(cls, entry: PersistentObject):
        raise NotImplementedError('cron jobs are immutable')


    @classmethod
    def delete(cls, id: int):
        client = DbClient.instance(cls.db_name())
        table = cls.table()

        try:
            client.txIMMEDIATE()

            sql = f'DELETE FROM {table} WHERE id = ?'
            client.execute(sql, data=(id,))

            client.txCOMMIT()

        except Exception as ex:
            client.txROLLBACK(ex)
