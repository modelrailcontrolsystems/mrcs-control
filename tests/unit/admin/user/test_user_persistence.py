"""
Created on 29 Nov 2025

@author: Bruno Beloff (bbeloff@me.com)

python -m unittest -v mrcs-core/tests/unit/admin/user/test_user_persistence.py

https://realpython.com/python-testing/
https://www.jetbrains.com/help/pycharm/creating-tests.html
"""

import json
import os
import unittest

from mrcs_control.admin.user.user import PersistentUser
from mrcs_control.db.dbclient import DBClient, DBMode

from setup import Setup


# --------------------------------------------------------------------------------------------------------------------

class TestUserPersistence(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        DBClient.set_client_db_mode(DBMode.TEST)
        Setup.dbSetup()


    def test_insert(self):
        obj1, _ = self.__setup_db()
        records = list(PersistentUser.find_all())
        obj2 = records[0]

        self.assertEqual(obj2.email, obj1.email)


    def test_find(self):
        obj1, _ = self.__setup_db()
        obj2 = PersistentUser.find(obj1.uid)

        self.assertEqual(obj2.email, obj1.email)


    def test_update(self):
        obj1, _ = self.__setup_db()
        obj2 = PersistentUser(obj1.uid, obj1.email, obj1.role, obj1.must_set_password,
                              'Mickey', 'Mouse', obj1.created, obj1.latest_login)
        obj2.save()
        obj3 = PersistentUser.find(obj1.uid)

        self.assertEqual(obj3.given_name, 'Mickey')
        self.assertEqual(obj3.family_name, 'Mouse')


    def test_delete(self):
        _, obj2 = self.__setup_db()
        PersistentUser.delete(obj2.uid)
        obj3 = PersistentUser.find(obj2.uid)

        self.assertEqual(obj3, None)


    def test_log_in(self):
        obj1, _ = self.__setup_db()
        user = obj1.log_in(obj1.email, 'pass')
        self.assertIsNotNone(user)

        user = obj1.log_in(obj1.email, 'junk')
        self.assertIsNone(user)


    def test_set_password(self):
        obj1, _ = self.__setup_db()
        obj1.set_password(obj1.uid, 'admin')
        user = obj1.log_in(obj1.email, 'admin')
        self.assertIsNotNone(user)


    def test_email(self):
        obj1, _ = self.__setup_db()
        self.assertEqual(PersistentUser.email_in_use(obj1.email), True)
        self.assertEqual(PersistentUser.email_in_use('xbeloff@me.com'), False)


    # ----------------------------------------------------------------------------------------------------------------

    @classmethod
    def __setup_db(cls):
        PersistentUser.recreate_tables()

        abs_filename = os.path.join(os.path.dirname(__file__), 'data', 'new_user1.json')
        with open(abs_filename) as fp:
            jdict = json.load(fp)
        obj1 = PersistentUser.construct_from_jdict(jdict)
        obj1 = obj1.save(password='pass')

        abs_filename = os.path.join(os.path.dirname(__file__), 'data', 'new_user2.json')
        with open(abs_filename) as fp:
            jdict = json.load(fp)
        obj2 = PersistentUser.construct_from_jdict(jdict)
        obj2 = obj2.save(password='pass')

        return obj1, obj2


if __name__ == "__main_":
    unittest.main()
