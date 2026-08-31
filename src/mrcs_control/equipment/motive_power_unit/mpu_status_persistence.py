"""
Created on 4 Jul 2026

@author: Bruno Beloff (bbeloff@me.com)

SQLite database management for MPU status
"""

from abc import ABC
from typing import List, Self

from mrcs_control.data.persistence import PersistentObject
from mrcs_control.db.db_client import DbClient
from mrcs_control.db.db_name import DbName
from mrcs_core.equipment.motive_power_unit.mpu_configuration_report import MPUConfigurationReport
from mrcs_core.equipment.motive_power_unit.mpu_decoder_report import MPUDecoderReport
from mrcs_core.equipment.motive_power_unit.mpu_enums import MPUDirection


# --------------------------------------------------------------------------------------------------------------------

class MPUStatusPersistence(PersistentObject, ABC):
    """
    SQLite database management for MPU status
    """

    __DB_NAME = DbName.MPU

    __TABLE_NAME = 'mpus'
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
            label TEXT PRIMARY KEY, 
            address INTEGER UNIQUE, 
            functions TEXT,
            speed_setting INTEGER,
            speed INTEGER,
            direction TEXT)
            '''
        client.execute(sql)


    @classmethod
    def _drop_tables(cls, client):
        table = cls.table()
        sql = f'DROP TABLE IF EXISTS {table}'
        client.execute(sql)


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def find_addresses(cls) -> List[int]:
        client = DbClient.instance(cls.db_name())

        table = cls.table()
        sql = f'SELECT address FROM {table} ORDER BY address'
        client.execute(sql)
        rows = client.fetchall()

        return [row[0] for row in rows]


    @classmethod
    def find_all(cls) -> List[Self]:
        client = DbClient.instance(cls.db_name())

        table = cls.table()
        sql = f'SELECT label, address, functions, speed_setting, speed, direction FROM {table} ORDER BY label'
        client.execute(sql)
        rows = client.fetchall()

        return [cls.construct_from_db(row) for row in rows]


    @classmethod
    def find_by_address(cls, address: int) -> Self | None:
        client = DbClient.instance(cls.db_name())

        table = cls.table()
        sql = f'SELECT label, address, functions, speed_setting, speed, direction FROM {table} WHERE address = ?'
        client.execute(sql, data=(address,))
        row = client.fetchone()

        if not row:
            return None

        return cls.construct_from_db(row)


    @classmethod
    def find(cls, label: str) -> Self | None:
        client = DbClient.instance(cls.db_name())

        table = cls.table()
        sql = f'SELECT label, address, functions, speed_setting, speed, direction FROM {table} WHERE label = ?'
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
    def insert(cls, item: PersistentObject) -> None:  # TODO: parameter should be MPUDesign
        client = DbClient.instance(cls.db_name())

        try:
            client.txIMMEDIATE()

            table = cls.table()
            sql = (f'REPLACE INTO {table} (label, address, functions, speed_setting, speed, direction) '
                   f'VALUES (?, ?, ?, ?, ?, ?)')
            client.execute(sql, data=item.as_db_insert())

            client.txCOMMIT()

        except Exception as exc:
            client.txROLLBACK(exc)
            raise


    @classmethod
    def update_from_configuration_report(cls, config: MPUConfigurationReport) -> Self:
        client = DbClient.instance(cls.db_name())

        try:
            client.txIMMEDIATE()

            table = cls.table()
            sql = f'UPDATE {table} SET functions = ? , speed_setting = ?, direction = ? WHERE address = ?'
            client.execute(sql,
                           data=(config.functions.as_json(), config.speed_setting,
                                 MPUDirection.from_reverse(config.reverse).name, config.mpu_address))

            sql = f'SELECT label, address, functions, speed_setting, speed, direction FROM {table} WHERE address = ?'
            client.execute(sql, data=(config.mpu_address,))
            row = client.fetchone()

            if not row:
                raise KeyError(f'no MPUStatus with address 0x{config.mpu_address:02x}')

            client.txCOMMIT()

            return cls.construct_from_db(row)

        except Exception as exc:
            client.txROLLBACK(exc)
            raise


    @classmethod
    def update_from_decoder_report(cls, decoder: MPUDecoderReport) -> Self:
        client = DbClient.instance(cls.db_name())

        try:
            client.txIMMEDIATE()

            table = cls.table()
            sql = f'UPDATE {table} SET speed = ? WHERE address = ?'
            client.execute(sql, data=(decoder.speed, decoder.mpu_address))

            sql = f'SELECT label, address, functions, speed_setting, speed, direction FROM {table} WHERE address = ?'
            client.execute(sql, data=(decoder.mpu_address,))
            row = client.fetchone()

            if not row:
                raise KeyError(f'no MPUStatus with address 0x{decoder.mpu_address:02x}')

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
