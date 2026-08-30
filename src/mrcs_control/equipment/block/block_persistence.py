"""
Created on 29 Nov 2025

@author: Bruno Beloff (bbeloff@me.com)

SQLite database management for BlockStatus
"""

from abc import ABC
from typing import List, Self

from mrcs_control.data.persistence import PersistentObject
from mrcs_control.db.db_client import DbClient
from mrcs_control.db.db_name import DbName
from mrcs_core.equipment.block.block_id import BlockID
from mrcs_core.equipment.block.block_report import BlockOccupancyReport, BlockVoltageReport


# --------------------------------------------------------------------------------------------------------------------

class BlockPersistence(PersistentObject, ABC):
    """
    SQLite database management for BlockStatus
    """

    __DB_NAME = DbName.Track

    __BLOCK_TABLE_NAME = 'blocks'
    __BLOCK_TABLE_VERSION = 1

    __OCCUPANT_TABLE_NAME = 'block_occupants'
    __OCCUPANT_TABLE_VERSION = 1


    @classmethod
    def db_name(cls) -> DbName:
        return cls.__DB_NAME


    @classmethod
    def block_table(cls):
        return f'{cls.__BLOCK_TABLE_NAME}_v{cls.__BLOCK_TABLE_VERSION}'


    @classmethod
    def occupant_table(cls):
        return f'{cls.__OCCUPANT_TABLE_NAME}_v{cls.__OCCUPANT_TABLE_VERSION}'


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def _create_tables(cls, client: DbClient):
        table = cls.block_table()
        sql = f'''
            CREATE TABLE IF NOT EXISTS {table} (
            label TEXT PRIMARY KEY, 
            address TEXT UNIQUE, 
            direction TEXT, 
            voltage TEXT)
            '''
        client.execute(sql)

        table = cls.occupant_table()
        sql = f'''
            CREATE TABLE IF NOT EXISTS {table} (
            block_label TEXT, 
            mpu_address TEXT, 
            face TEXT,
            CONSTRAINT pk_{table} PRIMARY KEY (block_label, mpu_address),
            FOREIGN KEY (block_label) REFERENCES {cls.block_table()}(label) ON DELETE CASCADE)
            '''
        client.execute(sql)

        sql = f'CREATE INDEX IF NOT EXISTS {table}_block_label ON {table}(block_label)'
        client.execute(sql)


    @classmethod
    def _drop_tables(cls, client):
        table = cls.occupant_table()
        sql = f'DROP INDEX IF EXISTS {table}_block_label'
        client.execute(sql)

        sql = f'DROP TABLE IF EXISTS {table}'
        client.execute(sql)

        table = cls.block_table()
        sql = f'DROP TABLE IF EXISTS {table}'
        client.execute(sql)


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def find_all(cls) -> List[Self]:
        client = DbClient.instance(cls.db_name())

        table = cls.block_table()
        sql = f'SELECT label, address, direction, voltage FROM {table} ORDER BY label'
        client.execute(sql)
        block_rows = client.fetchall()

        if not block_rows:
            return []

        table = cls.occupant_table()
        sql = f'SELECT block_label, mpu_address, face FROM {table}'
        client.execute(sql)
        occupant_rows = client.fetchall()

        occupants = {block_row[0]: [] for block_row in block_rows}

        for occupant_row in occupant_rows:
            occupants[occupant_row[0]].append(occupant_row[1:])

        return [cls.construct_from_db(block_row, *occupants[block_row[0]]) for block_row in block_rows]


    @classmethod
    def find(cls, label: str) -> Self | None:
        client = DbClient.instance(cls.db_name())

        table = cls.block_table()
        sql = f'SELECT label, address, direction, voltage FROM {table} WHERE label = ?'
        client.execute(sql, data=(label,))
        block_row = client.fetchone()

        if not block_row:
            return None

        table = cls.occupant_table()
        sql = f'SELECT mpu_address, face FROM {table} WHERE block_label = ?'
        client.execute(sql, data=(label,))
        occupant_rows = client.fetchall()

        return cls.construct_from_db(block_row, *occupant_rows)


    @classmethod
    def exists(cls, label: str) -> bool:
        client = DbClient.instance(cls.db_name())

        table = cls.block_table()
        sql = f'SELECT label FROM {table} WHERE label = ?'
        client.execute(sql, data=(label,))
        row = client.fetchone()

        return row is not None


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def insert(cls, item: PersistentObject) -> None:  # TODO: parameter should be BlockDesign
        client = DbClient.instance(cls.db_name())

        try:
            client.txIMMEDIATE()

            label = item.as_db_insert()[0]

            table = cls.block_table()
            sql = f'REPLACE INTO {table} (label, address, direction, voltage) VALUES (?, ?, ?, ?)'
            client.execute(sql, data=item.as_db_insert())

            # any existing occupants are deleted by cascade on REPLACE

            table = cls.occupant_table()
            for occupant in item.children():
                sql = f'INSERT INTO {table} (block_label, mpu_address, face) VALUES (?, ?, ?)'
                client.execute(sql, data=(label, *occupant.as_db_insert()))

            client.txCOMMIT()

        except Exception as exc:
            client.txROLLBACK(exc)
            raise


    @classmethod
    def update_from_voltage(cls, report: BlockVoltageReport) -> Self:
        client = DbClient.instance(cls.db_name())

        try:
            client.txIMMEDIATE()

            table = cls.block_table()
            sql = f'UPDATE {table} SET voltage = ? WHERE address = ?'
            client.execute(sql, data=(report.voltage.name, report.block_address))

            sql = f'SELECT label, address, direction, voltage FROM {table} WHERE address = ?'
            client.execute(sql, data=(report.block_address,))
            block_row = client.fetchone()

            if not block_row:
                raise KeyError(f'no BlockStatus with address {report.block_address}')

            table = cls.occupant_table()
            sql = f'SELECT mpu_address, face FROM {table} WHERE block_label = ?'
            client.execute(sql, data=(block_row[0],))
            occupant_rows = client.fetchall()

            client.txCOMMIT()

            return cls.construct_from_db(block_row, *occupant_rows)

        except Exception as exc:
            client.txROLLBACK(exc)
            raise


    @classmethod
    def update_from_block_occupancy_report(cls, report: BlockOccupancyReport) -> None:
        client = DbClient.instance(cls.db_name())

        cls.delete_occupants(report.block_id)

        try:
            client.txIMMEDIATE()

            occupant_table = cls.occupant_table()
            block_table = cls.block_table()

            for occupant in report.occupants:
                sql = (f'INSERT INTO {occupant_table} (block_label, mpu_address, face) '
                       f'VALUES ((SELECT label FROM {block_table} WHERE address = ?), ?, ?)')
                client.execute(sql, data=(report.block_id.block_address, occupant.mpu_address, occupant.face.name))

            client.txCOMMIT()

        except Exception as exc:
            client.txROLLBACK(exc)
            raise


    @classmethod
    def delete_block(cls, label: str) -> None:
        client = DbClient.instance(cls.db_name())

        try:
            client.txIMMEDIATE()

            table = cls.block_table()
            sql = f'DELETE FROM {table} WHERE label = ?'
            client.execute(sql, data=(label,))

            client.txCOMMIT()

        except Exception as exc:
            client.txROLLBACK(exc)
            raise


    @classmethod
    def delete_occupants(cls, block_id: BlockID) -> None:
        client = DbClient.instance(cls.db_name())

        try:
            client.txIMMEDIATE()

            occupant_table = cls.occupant_table()
            block_table = cls.block_table()

            sql = (f'DELETE FROM {occupant_table} '
                   f'WHERE block_label = (SELECT label FROM {block_table} WHERE address = ?)')
            client.execute(sql, data=(block_id.block_address,))

            client.txCOMMIT()

        except Exception as exc:
            client.txROLLBACK(exc)
            raise
