"""
Created on 19 Dec 2025

@author: Bruno Beloff (bbeloff@me.com)

Set up tests to use the test DB
"""

from mrcs_control.db.db_client import DbClient, DbMode


# --------------------------------------------------------------------------------------------------------------------

class Setup(object):
    """
    Set up tests to use the test DB
    """

    @classmethod
    def dbSetup(cls):
        if DbClient.client_db_mode() == DbMode.TEST:
            return

        DbClient.kill_all()
        DbClient.set_client_db_mode(DbMode.TEST)
