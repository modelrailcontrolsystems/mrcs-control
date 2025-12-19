"""
Created on 19 Dec 2025

@author: Bruno Beloff (bbeloff@me.com)

A structured representation of a user

{
  "uid": "c69a665c-11b5-4755-a903-97095f9dc915",
  "email": "bbeloff@me.com",
  "role": "ADMIN",
  "must_set_password": true,
  "given_name": "Bruno",
  "family_name": "Beloff",
  "created": "2025-11-30T09:36:23.553+00:00",
  "latest_login": null
}
"""

from mrcs_control.admin.user.user_persistence import UserPersistence
from mrcs_control.data.persistence import PersistentObject

from mrcs_core.admin.user.user import User, UserRole
from mrcs_core.data.iso_datetime import ISODatetime


# --------------------------------------------------------------------------------------------------------------------

class PersistentUser(User, UserPersistence, PersistentObject):
    """
    a structured representation of a user
    """

    @classmethod
    def construct_from_db(cls, uid, email, role, must_set_password, given_name, family_name, created, latest_login):
        uid = uid
        email = email
        role = UserRole(role)
        must_set_password = bool(must_set_password)
        given_name = given_name
        family_name = family_name
        created = ISODatetime.construct_from_db(created)
        latest_login = ISODatetime.construct_from_db(latest_login)

        return cls(uid, email, role, must_set_password, given_name, family_name, created, latest_login)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, uid: str | None, email: str, role: UserRole, must_set_password: bool,
                 given_name: str, family_name: str, created: ISODatetime | None, latest_login: ISODatetime | None):
        super().__init__(uid, email, role, must_set_password, given_name, family_name, created, latest_login)


    # ----------------------------------------------------------------------------------------------------------------

    def save(self, password=None):
        if self.uid is None:
            if password is None:
                raise ValueError('insert requires password')
            return super().insert(self, password=password)

        return super().update(self)


    # ----------------------------------------------------------------------------------------------------------------

    def as_db_insert(self):
        return self.email, self.role, self.must_set_password, self.given_name, self.family_name


    def as_db_update(self):
        return self.email, self.given_name, self.family_name, self.uid
