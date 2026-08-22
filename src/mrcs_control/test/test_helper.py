"""
Created on 19 Dec 2025

@author: Bruno Beloff (bbeloff@me.com)

Setup and tear down for tests using DB
"""

from mrcs_control.db.db_client import DbClient, DbMode


# --------------------------------------------------------------------------------------------------------------------

class TestHelper(object):
    """
    Setup and tear down for tests using DB
    """


    @classmethod
    def dbSetup(cls):
        if DbClient.client_db_mode() == DbMode.TEST:
            return

        DbClient.kill_all()
        DbClient.set_client_db_mode(DbMode.TEST)


    @classmethod
    def dbTeardown(cls):
        DbClient.kill_all()
