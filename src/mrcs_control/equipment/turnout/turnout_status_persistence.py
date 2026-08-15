"""
Created on 6 Jul 2026

@author: Bruno Beloff (bbeloff@me.com)

SQLite database management for turnout states
"""

from abc import ABC
from typing import List, Self

from mrcs_control.data.persistence import PersistentObject
from mrcs_control.db.db_client import DbClient
from mrcs_control.db.db_name import DbName
from mrcs_core.equipment.turnout.turnout_report import TurnoutReport


# --------------------------------------------------------------------------------------------------------------------

class TurnoutStatusPersistence(PersistentObject, ABC):
    """
    SQLite database management for MPU states
    """

    __DB_NAME = DbName.Track

    __TABLE_NAME = 'turnouts'
    __TABLE_VERSION = 1


    @classmethod
    def db_name(cls) -> DbName:
        return cls.__DB_NAME


    @classmethod
    def table(cls):
        return f'{cls.__TABLE_NAME}_v{cls.__TABLE_VERSION}'


    # ----------------------------------------------------------------------------------------------------------------

    # TODO: BlockStatusPersistence must be built before this table

    @classmethod
    def _create_tables(cls, client: DbClient):
        table = cls.table()
        sql = f'''
            CREATE TABLE IF NOT EXISTS {table} (
            label TEXT PRIMARY KEY, 
            block_label TEXT, 
            address INTEGER UNIQUE, 
            position TEXT)
            '''
        # TODO: re-instate constraint when block_node is built
        # FOREIGN KEY (block_label) REFERENCES {BlockStatusPersistence.block_table()}(label) ON DELETE CASCADE)
        client.execute(sql)


    @classmethod
    def _drop_tables(cls, client):
        table = cls.table()
        sql = f'DROP TABLE IF EXISTS {table}'
        client.execute(sql)


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def find_all(cls) -> List[Self]:
        client = DbClient.instance(cls.db_name())

        table = cls.table()
        sql = f'SELECT label, block_label, address, position FROM {table} ORDER BY block_label, label'
        client.execute(sql)
        rows = client.fetchall()

        return [cls.construct_from_db(row) for row in rows]


    @classmethod
    def find_for_block(cls, block_label: str) -> List[Self]:
        client = DbClient.instance(cls.db_name())

        table = cls.table()
        sql = f'SELECT label, block_label, address, position FROM {table} WHERE block_label = ? ORDER BY label'
        client.execute(sql, data=(block_label,))
        rows = client.fetchall()

        return [cls.construct_from_db(row) for row in rows]


    @classmethod
    def find_by_address(cls, address: int) -> Self | None:
        client = DbClient.instance(cls.db_name())

        table = cls.table()
        sql = f'SELECT label, block_label, address, position FROM {table} WHERE address = ?'
        client.execute(sql, data=(address,))
        row = client.fetchone()

        if not row:
            return None

        return cls.construct_from_db(row)


    @classmethod
    def find(cls, label: str) -> Self | None:
        client = DbClient.instance(cls.db_name())

        table = cls.table()
        sql = f'SELECT label, block_label, address, position FROM {table} WHERE label = ?'
        client.execute(sql, data=(label,))
        row = client.fetchone()

        if not row:
            return None

        return cls.construct_from_db(row)


    @classmethod
    def exists(cls, label: str) -> bool:
        client = DbClient.instance(cls.db_name())

        table = cls.table()
        sql = f'SELECT label FROM {table} WHERE label = ?'
        client.execute(sql, data=(label,))
        row = client.fetchone()

        return row is not None


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def insert(cls, item: PersistentObject) -> None:  # TODO: parameter should be TurnoutDesign
        client = DbClient.instance(cls.db_name())

        try:
            client.txIMMEDIATE()

            table = cls.table()
            sql = f'REPLACE INTO {table} (label, block_label, address, position) VALUES (?, ?, ?, ?)'
            client.execute(sql, data=item.as_db_insert())

            client.txCOMMIT()

        except Exception as exc:
            client.txROLLBACK(exc)
            raise


    @classmethod
    def update_from_turnout_report(cls, report: TurnoutReport) -> Self:
        client = DbClient.instance(cls.db_name())

        try:
            client.txIMMEDIATE()

            table = cls.table()
            sql = f'UPDATE {table} SET position = ? WHERE address = ?'
            client.execute(sql, data=(report.position.name, report.turnout_address))

            sql = f'SELECT label, block_label, address, position FROM {table} WHERE address = ?'
            client.execute(sql, data=(report.turnout_address,))
            row = client.fetchone()

            if not row:
                raise KeyError(f'no TurnoutStatus with address {report.turnout_address}')

            client.txCOMMIT()

            return cls.construct_from_db(row)

        except Exception as exc:
            client.txROLLBACK(exc)
            raise


    @classmethod
    def delete(cls, label: str) -> None:
        client = DbClient.instance(cls.db_name())

        try:
            client.txIMMEDIATE()

            table = cls.table()
            sql = f'DELETE FROM {table} WHERE label = ?'
            client.execute(sql, data=(label,))

            client.txCOMMIT()

        except Exception as exc:
            client.txROLLBACK(exc)
            raise
