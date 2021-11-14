"""
    Copyright (c) 2020 - present NekrodNIK, Stepan Skriabin, rus-ai and other.
    Look at the file AUTHORS.md(located at the root of the project) to get the
    full list.

    This file is part of Morelia Server.

    Morelia Server is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Morelia Server is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with Morelia Server. If not, see <https://www.gnu.org/licenses/>.
"""

import unittest
from loguru import logger

from sqlobject.main import SQLObject, SelectResults

from mod.db.dbhandler import DBHandler  # noqa
from mod.db import models  # noqa
from mod.db.dbhandler import DatabaseAccessError  # noqa
from mod.db.dbhandler import DatabaseWriteError  # noqa
from mod.db.dbhandler import DatabaseReadError  # noqa


class TestDBHandlerMainMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        logger.remove()
        cls.db = DBHandler(uri="sqlite:/:memory:")

    def setUp(self):
        self.db.create()

    def tearDown(self):
        self.db.delete()

    def test_create_database(self):
        dbquery = self.db.get_all_user()
        self.assertIsInstance(dbquery, SelectResults)

    def test_delete_database(self):
        self.db.delete()
        self.assertRaises(DatabaseAccessError,
                          self.db.get_admin_by_name,
                          username="User")

    def test_search_db_in_models(self):
        self.db.delete()
        dbquery = self.db._DBHandler__search_db_in_models()
        self.assertIsInstance(dbquery, tuple)
        self.assertEqual(dbquery[0], 'Admin')

    def test_create_db_not_set_debug(self):
        self.db.delete()
        db = DBHandler(uri="sqlite:/:memory:")
        self.assertFalse(db.debug)
        self.assertEqual(db._uri,
                         "sqlite:/:memory:")

    def test_create_db_set_debug(self):
        self.db.delete()
        db = DBHandler(uri="sqlite:/:memory:",
                       debug=True)
        self.assertFalse(db.debug)
        self.assertEqual(db._uri,
                         "sqlite:/:memory:")

    def test_create_db_set_debug_logger(self):
        self.db.delete()
        db = DBHandler(uri="sqlite:/:memory:",
                       debug=True,
                       logger='Test')
        self.assertFalse(db.debug)
        self.assertEqual(db._uri,
                         "sqlite:/:memory:")

    def test_create_db_set_debug_logger_loglevel(self):
        db = DBHandler(uri="sqlite:/:memory:",
                       debug=True,
                       logger='Test',
                       loglevel='debug')
        self.assertTrue(db.debug)
        self.assertEqual(db._uri,
                         "sqlite:/:memory:?debug=1?logger=Test?loglevel=debug")

    def test_str(self):
        self.assertEqual(str(self.db),
                         "Connected to database: sqlite:/:memory:")

    def test_repr(self):
        self.assertEqual(repr(self.db),
                         "class DBHandler: debug=0 logger=None loglevel=None")


class TestDBHandlerMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()
        cls.db = DBHandler(uri="sqlite:/:memory:")

    def setUp(self):
        self.db.create()
        self.db.add_user(uuid="123456",
                         login="User1",
                         password="password",
                         hash_password="hash",
                         username="username",
                         salt=b"salt",
                         key=b"key")
        self.db.add_user(uuid="123457",
                         login="User2",
                         password="password",
                         hash_password="hash",
                         username="username",
                         salt=b"salt",
                         key=b"key")
        self.db.add_admin(username="User1",
                          hash_password="hash")
        self.db.add_admin(username="User2",
                          hash_password="hash")
        self.db.add_flow(uuid="6669",
                         users=["123456"],
                         time_created=5556669,
                         flow_type="Test",
                         title="test1",
                         info="TestTest",
                         owner="User1")
        self.db.add_flow(uuid="666999",
                         users=["123456"],
                         time_created=555666999,
                         flow_type="Test",
                         title="test2",
                         info="TestTest",
                         owner="User2")
        self.db.add_message(flow_uuid="6669",
                            user_uuid="123456",
                            message_uuid="111222",
                            time=123123,
                            text="Hello World!")
        self.db.add_message(flow_uuid="666999",
                            user_uuid="123457",
                            message_uuid="333444",
                            time=123124,
                            text="Hello World!")

    def tearDown(self):
        self.db.delete()

    def test_read_db(self):
        dbquery_one = self.db._DBHandler__read_db(table="UserConfig",
                                                  get_one=True,
                                                  uuid="123456")
        dbquery_many = self.db._DBHandler__read_db(table="UserConfig",
                                                   get_one=False,
                                                   username="username")
        self.assertEqual(dbquery_one.login, "User1")
        self.assertEqual(dbquery_many.count(), 2)
        self.assertIsInstance(dbquery_many,
                              SelectResults)
        self.assertRaises(DatabaseReadError,
                          self.db._DBHandler__read_db,
                          table="UserConfig",
                          get_one=True,
                          uuid="123459")
        self.db.delete()
        self.assertRaises(DatabaseAccessError,
                          self.db._DBHandler__read_db,
                          table="UserConfig",
                          get_one=True,
                          uuid="123459")

    def test_write_db(self):
        dbquery = self.db._DBHandler__write_db(table="UserConfig",
                                               uuid="123458",
                                               login="User2",
                                               password="password")
        self.assertIsInstance(dbquery, models.UserConfig)
        self.assertRaises(DatabaseWriteError,
                          self.db._DBHandler__write_db,
                          table="UserConfig",
                          uuid="123458",
                          login="User2",
                          password="password")

    def test_get_debug(self):
        self.assertFalse(self.db.debug)

    def test_set_debug(self):
        self.db.debug = True
        self.assertTrue(self.db.debug)

    def test_get_all_user(self):
        dbquery = self.db.get_all_user()
        self.assertIsInstance(dbquery,
                              SelectResults)
        self.assertEqual(dbquery[0].username, "username")

    def test_get_user_by_uuid(self):
        dbquery = self.db.get_user_by_uuid(uuid="123457")
        self.assertIsInstance(dbquery,
                              SQLObject)
        self.assertEqual(dbquery.login, "User2")

    def test_get_user_by_login(self):
        dbquery = self.db.get_user_by_login(login="User2")
        self.assertIsInstance(dbquery,
                              SQLObject)
        self.assertEqual(dbquery.uuid, "123457")

    def test_get_user_by_login_and_password(self):
        dbquery = self.db.get_user_by_login_and_password(login="User1",
                                                         password="password")
        self.assertIsInstance(dbquery,
                              SQLObject)
        self.assertEqual(dbquery.uuid, "123456")

    def test_new_user(self):
        dbquery = self.db.add_user(uuid="123458",
                                   login="Nick",
                                   password="password",
                                   hash_password="hash",
                                   username="username",
                                   salt=b"salt",
                                   key=b"key")
        self.assertIsInstance(dbquery,
                              SQLObject)
        self.assertEqual(dbquery.uuid, "123458")

    def test_update_user(self):
        new_login = "new_login"
        new_password = "new_password"
        new_hash = "new_hash"
        new_username = "new_username"
        new_is_bot = True
        new_auth_id = "new_auth_id"
        new_email = "new_email@email.com"
        new_avatar = b'avatar'
        new_bio = "new_bio"
        new_key = b"new_key"
        new_salt = b"new_salt"
        dbquery = self.db.update_user(uuid="123456",
                                      login=new_login,
                                      password=new_password,
                                      hash_password=new_hash,
                                      username=new_username,
                                      is_bot=new_is_bot,
                                      auth_id=new_auth_id,
                                      email=new_email,
                                      avatar=new_avatar,
                                      bio=new_bio,
                                      key=new_key,
                                      salt=new_salt)
        new_query = self.db.get_user_by_uuid(uuid="123456")
        self.assertIsInstance(dbquery,
                              str)
        self.assertEqual(dbquery, "Updated")
        self.assertEqual(new_query.login, new_login)
        self.assertEqual(new_query.password, new_password)
        self.assertEqual(new_query.hashPassword, new_hash)
        self.assertEqual(new_query.username, new_username)
        self.assertEqual(new_query.isBot, new_is_bot)
        self.assertEqual(new_query.authId, new_auth_id)
        self.assertEqual(new_query.email, new_email)
        self.assertEqual(new_query.avatar, new_avatar)
        self.assertEqual(new_query.bio, new_bio)
        self.assertEqual(new_query.key, new_key)
        self.assertEqual(new_query.salt, new_salt)

    def test_get_all_message(self):
        dbquery = self.db.get_all_message()
        self.assertIsInstance(dbquery,
                              SelectResults)
        self.assertEqual(dbquery[0].text, "Hello World!")

    def test_get_message_by_uuid(self):
        dbquery = self.db.get_message_by_uuid(uuid="111222")
        self.assertIsInstance(dbquery,
                              SQLObject)
        self.assertEqual(dbquery.time, 123123)

    def test_get_message_by_text(self):
        dbquery = self.db.get_message_by_text(text="Hello World!")
        self.assertIsInstance(dbquery,
                              SelectResults)
        self.assertEqual(dbquery[0].time, 123123)

    def test_get_message_by_exact_time(self):
        dbquery = self.db.get_message_by_exact_time(time=123124)
        self.assertIsInstance(dbquery,
                              SelectResults)
        self.assertEqual(dbquery[0].uuid, "333444")

    def test_get_message_by_less_time(self):
        dbquery = self.db.get_message_by_less_time(time=123124)
        self.assertIsInstance(dbquery,
                              SelectResults)
        self.assertEqual(dbquery[0].uuid, "111222")

    def test_get_message_by_more_time(self):
        dbquery = self.db.get_message_by_more_time(time=123124)
        self.assertIsInstance(dbquery,
                              SelectResults)
        self.assertEqual(dbquery[0].uuid, "333444")

    def test_get_message_by_more_time_and_flow(self):
        dbquery = self.db.get_message_by_more_time_and_flow(flow_uuid="6669",
                                                            time=123123)
        self.assertIsInstance(dbquery,
                              SelectResults)
        self.assertEqual(dbquery[0].uuid, "111222")

    def test_get_message_by_less_time_and_flow(self):
        dbquery = self.db.get_message_by_less_time_and_flow(flow_uuid="6669",
                                                            time=123124)
        self.assertIsInstance(dbquery,
                              SelectResults)
        self.assertEqual(dbquery[0].uuid, "111222")

    def test_get_message_by_exact_time_and_flow(self):
        dbquery = self.db.get_message_by_exact_time_and_flow(flow_uuid="6669",
                                                             time=123123)
        self.assertIsInstance(dbquery,
                              SelectResults)
        self.assertEqual(dbquery[0].uuid, "111222")

    def test_add_message(self):
        dbquery = self.db.add_message(flow_uuid="666999",
                                      user_uuid="123456",
                                      message_uuid="444555",
                                      time=123125,
                                      text="Hello World!")
        self.assertIsInstance(dbquery,
                              SQLObject)
        new_query = self.db.get_message_by_uuid(uuid="444555")
        self.assertEqual(new_query.time, 123125)

    def test_update_message(self):
        new_text = "new_text"
        new_picture = b"new_picture"
        new_video = b"new_video"
        new_audio = b"new_audio"
        new_document = b"new_document"
        new_emoji = b"new_emoji"
        new_edited_time = 123456
        new_edited_status = True
        dbquery = self.db.update_message(uuid="111222",
                                         text=new_text,
                                         picture=new_picture,
                                         video=new_video,
                                         audio=new_audio,
                                         document=new_document,
                                         emoji=new_emoji,
                                         edited_time=new_edited_time,
                                         edited_status=new_edited_status)
        new_query = self.db.get_message_by_uuid(uuid="111222")
        self.assertIsInstance(dbquery,
                              str)
        self.assertEqual(dbquery, "Updated")
        self.assertEqual(new_query.text, new_text)
        self.assertEqual(new_query.filePicture, new_picture)
        self.assertEqual(new_query.fileVideo, new_video)
        self.assertEqual(new_query.fileAudio, new_audio)
        self.assertEqual(new_query.fileDocument, new_document)
        self.assertEqual(new_query.emoji, new_emoji)
        self.assertEqual(new_query.editedTime, new_edited_time)
        self.assertEqual(new_query.editedStatus, new_edited_status)

    def test_get_all_flow(self):
        dbquery = self.db.get_all_flow()
        self.assertIsInstance(dbquery,
                              SelectResults)
        self.assertEqual(dbquery[0].info, "TestTest")

    def test_get_flow_by_title(self):
        dbquery = self.db.get_flow_by_title(title="test1")
        self.assertIsInstance(dbquery,
                              SelectResults)
        self.assertEqual(dbquery[0].info, "TestTest")

    def test_get_flow_by_uuid(self):
        dbquery = self.db.get_flow_by_uuid(uuid="666999")
        self.assertIsInstance(dbquery,
                              SQLObject)
        self.assertEqual(dbquery.owner, "User2")

    def test_get_flow_by_more_time(self):
        dbquery = self.db.get_flow_by_more_time(time=5556669)
        self.assertIsInstance(dbquery,
                              SelectResults)
        self.assertEqual(dbquery[0].flowType, "Test")

    def test_get_flow_by_less_time(self):
        dbquery = self.db.get_flow_by_less_time(time=555666999)
        self.assertIsInstance(dbquery,
                              SelectResults)
        self.assertEqual(dbquery[0].users[0].uuid, "123456")

    def test_get_flow_by_exact_time(self):
        dbquery = self.db.get_flow_by_exact_time(time=555666999)
        self.assertIsInstance(dbquery,
                              SelectResults)
        self.assertEqual(dbquery[0].title, "test2")

    def test_add_flow(self):
        self.db.add_user(uuid="123459",
                         login="User9",
                         password="password",
                         hash_password="hash",
                         username="username",
                         salt=b"salt",
                         key=b"key")
        dbquery = self.db.add_flow(uuid="666996",
                                   users=["123459"],
                                   time_created=555666996,
                                   flow_type="Test",
                                   title="test9",
                                   info="TestTest",
                                   owner="User9")
        self.assertIsInstance(dbquery,
                              SQLObject)
        self.assertEqual(dbquery.owner, "User9")
        self.assertEqual(dbquery.users[0].login, "User9")

    def test_update_flow(self):
        new_flow_type = "new_flow_type"
        new_title = "new_title"
        new_info = "new_info"
        new_owner = "new_owner"
        dbquery = self.db.update_flow(uuid="666999",
                                      flow_type=new_flow_type,
                                      title=new_title,
                                      info=new_info,
                                      owner=new_owner)
        self.assertIsInstance(dbquery,
                              str)
        self.assertEqual(dbquery, "Updated")
        new_query = self.db.get_flow_by_uuid(uuid="666999")
        self.assertEqual(new_query.flowType, new_flow_type)
        self.assertEqual(new_query.title, new_title)
        self.assertEqual(new_query.info, new_info)
        self.assertEqual(new_query.owner, new_owner)

    def test_table_count(self):
        dbquery = self.db.table_count()
        self.assertIsInstance(dbquery,
                              tuple)
        self.assertEqual(dbquery.user_count, 2)
        self.assertEqual(dbquery.flow_count, 2)
        self.assertEqual(dbquery.message_count, 2)

    def test_get_all_admin(self):
        dbquery = self.db.get_all_admin()
        self.assertIsInstance(dbquery,
                              SelectResults)
        self.assertEqual(dbquery[0].hashPassword, "hash")

    def test_get_admin_by_name(self):
        dbquery = self.db.get_admin_by_name(username="User2")
        self.assertIsInstance(dbquery,
                              SQLObject)
        self.assertEqual(dbquery.hashPassword, "hash")

    def test_add_admin(self):
        dbquery = self.db.add_admin(username="User3",
                                    hash_password="hash3")
        self.assertIsInstance(dbquery,
                              SQLObject)
        self.assertEqual(dbquery.hashPassword, "hash3")
