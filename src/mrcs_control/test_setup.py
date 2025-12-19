"""
Created on 19 Dec 2025

@author: Bruno Beloff (bbeloff@me.com)

Set up tests to use the test DB
"""

from mrcs_core.db.dbclient import DBClient, DBMode


# --------------------------------------------------------------------------------------------------------------------

class TestSetup(object):
    """
    Set up tests to use the test DB
    """

    @classmethod
    def dbSetup(cls):
        print('*** mrcs_control: dbSetup')

        if DBClient.client_db_mode() == DBMode.TEST:
            return

        DBClient.kill_all()
        DBClient.set_client_db_mode(DBMode.TEST)
