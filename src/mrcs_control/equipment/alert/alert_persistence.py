"""
Created on 15 Nov 2026

@author: Bruno Beloff (bbeloff@me.com)

SQLite database management for messages

https://forum.xojo.com/t/sqlite-return-id-of-record-inserted/37896/3
"""

from abc import ABC

from mrcs_control.data.persistence import PersistentObject
from mrcs_control.db.db_client import DbClient
from mrcs_control.db.db_name import DbName


# --------------------------------------------------------------------------------------------------------------------

class AlertPersistence(PersistentObject, ABC):
    """
    SQLite database management for messages
    """

    __DB_NAME = DbName.Alert

    __TABLE_NAME = 'alerts'
    __TABLE_VERSION = 1


    @classmethod
    def db_name(cls) -> DbName:
        return cls.__DB_NAME


    @classmethod
    def table(cls):
        return f'{cls.__TABLE_NAME}_v{cls.__TABLE_VERSION}'


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def _create_tables(cls, client: DbClient):
        table = cls.table()

        sql = f'''
            CREATE TABLE IF NOT EXISTS {table} (
            id INTEGER PRIMARY KEY, 
            severity TEXT NOT NULL, 
            impact TEXT NOT NULL, 
            subject TEXT NOT NULL, 
            text TEXT NOT NULL,
            raised_at TIMESTAMP NOT NULL, 
            resolved_at TIMESTAMP)
        '''
        client.execute(sql)

        sql = f'CREATE INDEX IF NOT EXISTS {table}_id ON {table}(id)'
        client.execute(sql)

        sql = f'CREATE INDEX IF NOT EXISTS {table}_severity ON {table}(severity)'
        client.execute(sql)

        sql = f'CREATE INDEX IF NOT EXISTS {table}_impact ON {table}(impact)'
        client.execute(sql)

        sql = f'CREATE INDEX IF NOT EXISTS {table}_subject ON {table}(subject)'
        client.execute(sql)

        sql = f'CREATE INDEX IF NOT EXISTS {table}_raised_at ON {table}(raised_at)'
        client.execute(sql)

        sql = f'CREATE INDEX IF NOT EXISTS {table}_resolved_at ON {table}(resolved_at)'
        client.execute(sql)


    @classmethod
    def _drop_tables(cls, client):
        table = cls.table()

        sql = f'DROP INDEX IF EXISTS {table}_id'
        client.execute(sql)

        sql = f'DROP INDEX IF EXISTS {table}_severity'
        client.execute(sql)

        sql = f'DROP INDEX IF EXISTS {table}_impact'
        client.execute(sql)

        sql = f'DROP INDEX IF EXISTS {table}_subject'
        client.execute(sql)

        sql = f'DROP INDEX IF EXISTS {table}_raised_at'
        client.execute(sql)

        sql = f'DROP INDEX IF EXISTS {table}_resolved_at'
        client.execute(sql)

        sql = f'DROP TABLE IF EXISTS {table}'
        client.execute(sql)


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def find_unresolved(cls):
        client = DbClient.instance(cls.db_name())
        table = cls.table()

        sql = f'SELECT * FROM {table} WHERE resolved_at IS NULL ORDER BY id'
        client.execute(sql)
        rows = client.fetchall()

        return (cls.construct_from_db(row) for row in rows)


    @classmethod
    def find_latest(cls, limit: int):
        client = DbClient.instance(cls.db_name())
        table = cls.table()

        sql = f'SELECT * FROM {table} WHERE id IN (SELECT id FROM {table} ORDER BY id DESC LIMIT {limit})'
        client.execute(sql)
        rows = client.fetchall()

        return (cls.construct_from_db(row) for row in rows)


    @classmethod
    def find_by_id(cls, id: int):
        client = DbClient.instance(cls.db_name())
        table = cls.table()

        sql = f'SELECT * FROM {table} WHERE id == ?'
        client.execute(sql, data=(id,))
        row = client.fetchone()

        return cls.construct_from_db(row) if row else None


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def insert(cls, alert: PersistentObject) -> int:
        client = DbClient.instance(cls.db_name())
        table = cls.table()

        try:
            client.txIMMEDIATE()

            sql = (f'INSERT INTO {table} (severity, impact, subject, text, raised_at, resolved_at) '
                   f'VALUES (?, ?, ?, ?, ?, ?)')
            client.execute(sql, data=alert.as_db_insert())

            sql = 'SELECT last_insert_rowid()'
            client.execute(sql)
            row = client.fetchone()

            client.txCOMMIT()

            return int(row[0])

        except Exception as exc:
            client.txROLLBACK(exc)
            raise


    @classmethod
    def update_resolved(cls, alert: PersistentObject) -> None:
        client = DbClient.instance(cls.db_name())
        table = cls.table()

        try:
            client.txIMMEDIATE()

            sql = f'UPDATE {table} SET resolved_at = ? WHERE id = ?'
            client.execute(sql, data=alert.as_db_update())

            client.txCOMMIT()

        except Exception as exc:
            client.txROLLBACK(exc)
            raise
