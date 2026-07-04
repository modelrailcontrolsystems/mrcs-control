"""
Created on 29 Nov 2025

@author: Bruno Beloff (bbeloff@me.com)

SQLite database management for users

make salt:
openssl rand -hex 32

https://www.geeksforgeeks.org/python/how-to-hash-passwords-in-python/
"""

import uuid
from abc import ABC

from pwdlib import PasswordHash

from mrcs_control.data.persistence import PersistentObject
from mrcs_control.db.db_client import DbClient
from mrcs_control.db.db_name import DbName
from mrcs_core.data.iso_datetime import ISODatetime


# --------------------------------------------------------------------------------------------------------------------

class UserPersistence(PersistentObject, ABC):
    """
    SQLite database management for users
    """

    __SALT = 'f0d655c131f2f64bd2203421515e940ccf6828f6d1595db92fb89507a3cd0bdf'


    @classmethod
    def hash_password(cls, password):
        return PasswordHash.recommended().hash(password, salt=cls.__SALT.encode())


    # ----------------------------------------------------------------------------------------------------------------

    __DB_NAME = DbName.Admin

    __TABLE_NAME = 'users'
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
            uid TEXT PRIMARY KEY , 
            email TEXT UNIQUE, 
            password TEXT, 
            role TEXT, 
            must_set_password INTEGER, 
            given_name TEXT, 
            family_name TEXT, 
            created TIMESTAMP NOT NULL DEFAULT(datetime('subsec')), 
            latest_login TIMESTAMP)
            '''
        client.execute(sql)

        sql = f'CREATE INDEX IF NOT EXISTS {table}_password ON {table}(password)'
        client.execute(sql)

        sql = f'CREATE INDEX IF NOT EXISTS {table}_given_name ON {table}(given_name)'
        client.execute(sql)

        sql = f'CREATE INDEX IF NOT EXISTS {table}_family_name ON {table}(family_name)'
        client.execute(sql)


    @classmethod
    def _drop_tables(cls, client):
        table = cls.table()

        sql = f'DROP INDEX IF EXISTS {table}_password'
        client.execute(sql)

        sql = f'DROP INDEX IF EXISTS {table}_given_name'
        client.execute(sql)

        sql = f'DROP INDEX IF EXISTS {table}_family_name'
        client.execute(sql)

        sql = f'DROP TABLE IF EXISTS {table}'
        client.execute(sql)


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def find_all(cls):
        client = DbClient.instance(cls.db_name())
        table = cls.table()

        sql = (f'SELECT uid, email, role, must_set_password, given_name, family_name, created, latest_login '
               f'FROM {table} ORDER BY family_name, given_name, email')
        client.execute(sql)
        rows = client.fetchall()

        return (cls.construct_from_db(*fields) for fields in rows)


    @classmethod
    def find(cls, uid):
        client = DbClient.instance(cls.db_name())
        table = cls.table()

        sql = (f'SELECT uid, email, role, must_set_password, given_name, family_name, created, latest_login '
               f'FROM {table} WHERE uid == ?')
        client.execute(sql, data=(uid,))
        row = client.fetchone()

        return cls.construct_from_db(*row) if row else None


    @classmethod
    def email_user(cls, email):
        client = DbClient.instance(cls.db_name())
        table = cls.table()

        sql = f'SELECT uid FROM {table} WHERE email == ?'
        client.execute(sql, data=(email,))
        row = client.fetchone()

        return row[0] if row else None


    @classmethod
    def exists(cls, uid):
        client = DbClient.instance(cls.db_name())
        table = cls.table()

        sql = f'SELECT uid FROM {table} WHERE uid == ?'
        client.execute(sql, data=(uid,))
        row = client.fetchone()

        return row is not None


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def insert(cls, item: PersistentObject, password=None):
        client = DbClient.instance(cls.db_name())
        table = cls.table()

        uid = str(uuid.uuid4())
        hashed_password = cls.hash_password(password)
        data = [uid, hashed_password] + list(item.as_db_insert())

        try:
            client.txIMMEDIATE()

            sql = (f'INSERT INTO {table} (uid, password, email, role, must_set_password, given_name, family_name) '
                   f'VALUES (?, ?, ?, ?, ?, ?, ?)')
            client.execute(sql, data=data)

            client.txCOMMIT()

            sql = (f'SELECT uid, email, role, must_set_password, given_name, family_name, created, latest_login '
                   f'FROM {table} WHERE uid == ?')
            client.execute(sql, data=(uid,))
            row = client.fetchone()

            return cls.construct_from_db(*row)

        except Exception as ex:
            client.txROLLBACK(ex)


    @classmethod
    def update(cls, item: PersistentObject):
        client = DbClient.instance(cls.db_name())
        table = cls.table()

        try:
            client.txIMMEDIATE()

            sql = f'UPDATE {table} SET email = ?, given_name = ?, family_name = ? WHERE uid = ?'  # TODO: set role also
            client.execute(sql, data=(item.as_db_update()))

            client.txCOMMIT()

        except Exception as ex:
            client.txROLLBACK(ex)


    @classmethod
    def delete(cls, uid: str):
        client = DbClient.instance(cls.db_name())
        table = cls.table()

        try:
            client.txIMMEDIATE()

            sql = f'SELECT role FROM {table} WHERE uid == ?'
            client.execute(sql, data=(uid,))
            row = client.fetchone()

            if row is None:
                client.txCOMMIT()
                return

            if row[0] == 'ADMIN':
                sql = f'SELECT COUNT(uid) FROM {table} WHERE role == "ADMIN"'
                client.execute(sql)
                row = client.fetchone()

                if int(row[0]) < 2:
                    raise RuntimeError('there must be at least one ADMIN user')

            sql = f'DELETE FROM {table} WHERE uid = ?'
            client.execute(sql, data=(uid,))

            client.txCOMMIT()

        except Exception as ex:
            client.txROLLBACK(ex)


    @classmethod
    def log_in(cls, email, password):
        client = DbClient.instance(cls.db_name())
        table = cls.table()

        hashed_password = cls.hash_password(password)

        try:
            client.txIMMEDIATE()

            sql = f'SELECT uid FROM {table} WHERE email == ? AND password == ?'
            client.execute(sql, data=(email, hashed_password))
            row = client.fetchone()

            if not row:
                client.txCOMMIT()
                return None

            uid = row[0]

            sql = f'UPDATE {table} SET latest_login = ? WHERE uid = ?'
            client.execute(sql, data=(ISODatetime.now().dbformat(), uid))

            client.txCOMMIT()

            sql = (f'SELECT uid, email, role, must_set_password, given_name, family_name, created, latest_login '
                   f'FROM {table} WHERE uid == ?')
            client.execute(sql, data=(uid,))
            row = client.fetchone()

            return cls.construct_from_db(*row)

        except Exception as ex:
            client.txROLLBACK(ex)


    @classmethod
    def set_password(cls, uid, password):
        client = DbClient.instance(cls.db_name())
        table = cls.table()

        hashed_password = cls.hash_password(password)

        try:
            client.txIMMEDIATE()

            sql = f'UPDATE {table} SET password = ?, must_set_password = 0  WHERE uid = ?'
            client.execute(sql, data=(hashed_password, uid))

            client.txCOMMIT()

        except Exception as ex:
            client.txROLLBACK(ex)
