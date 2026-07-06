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

    Admin = 'Admin'  # users
    Block = 'Block'  # BlockStatus
    Cron = 'Cron'  # cron and crontab
    MessageLog = 'MessageLog'  # message recorder
    MPU = 'MPU'  # motive power units
    Test = 'Test'  # used by unit tests
