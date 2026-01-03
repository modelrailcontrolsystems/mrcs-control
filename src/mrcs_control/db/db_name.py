"""
Created on 2 Jan 2026

@author: Bruno Beloff (bbeloff@me.com)

SQLite databases used by mrcs_control
"""

from enum import StrEnum


# --------------------------------------------------------------------------------------------------------------------

class DbName(StrEnum):
    """
    SQLite databases used by mrcs_control
    """

    Admin = 'Admin'                     # users
    Cron = 'Cron'                       # cron and crontab
    MessageLog = 'MessageLog'           # message recorder
    Test = 'Test'                       # used by unit tests
