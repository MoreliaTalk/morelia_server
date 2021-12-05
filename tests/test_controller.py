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

import json
import os
import unittest
import configparser
from uuid import uuid4

from loguru import logger

from mod import api  # noqa
from mod import controller  # noqa
from mod import lib  # noqa
from mod.db.dbhandler import DBHandler  # noqa
from mod.controller import ProtocolMethods
from mod.db.dbhandler import DatabaseAccessError
from mod.db.dbhandler import DatabaseReadError
from mod.db.dbhandler import DatabaseWriteError

# Add path to directory with code being checked
# to variable 'PATH' to import modules from directory
# above the directory with the tests.
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
FIXTURES_PATH = os.path.join(BASE_PATH, "fixtures")

GET_UPDATE = os.path.join(FIXTURES_PATH, "get_update.json")
SEND_MESSAGE = os.path.join(FIXTURES_PATH, "send_message.json")
ALL_MESSAGES = os.path.join(FIXTURES_PATH, "all_message.json")
ADD_FLOW = os.path.join(FIXTURES_PATH, "add_flow.json")
ALL_FLOW = os.path.join(FIXTURES_PATH, "all_flow.json")
USER_INFO = os.path.join(FIXTURES_PATH, "user_info.json")
REGISTER_USER = os.path.join(FIXTURES_PATH, "register_user.json")
AUTH = os.path.join(FIXTURES_PATH, "auth.json")
DELETE_USER = os.path.join(FIXTURES_PATH, "delete_user.json")
DELETE_MESSAGE = os.path.join(FIXTURES_PATH, "delete_message.json")
EDITED_MESSAGE = os.path.join(FIXTURES_PATH, "edited_message.json")
PING_PONG = os.path.join(FIXTURES_PATH, "ping_pong.json")
ERRORS = os.path.join(FIXTURES_PATH, "errors.json")
NON_VALID_ERRORS = os.path.join(FIXTURES_PATH, "non_valid_errors.json")
ERRORS_ONLY_TYPE = os.path.join(FIXTURES_PATH, "errors_only_type.json")


# ************** Read "config.ini" ********************
config = configparser.ConfigParser()
config.read('config.ini')
limit = config['SERVER_LIMIT']
# ************** END **********************************


class TestCheckAuthToken(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()
        cls.db = DBHandler(uri="sqlite:/:memory:")

    def setUp(self):
        self.db.create()
        self.db.add_user(uuid="123456",
                         login="login",
                         password="password",
                         auth_id="auth_id")
        self.test = api.Request.parse_file(SEND_MESSAGE)

    def tearDown(self):
        self.db.delete()
        del self.test

    def test_check_auth(self):
        run_method = ProtocolMethods('test',
                                   database=self.db)
        check_auth = run_method._check_auth('123456',
                                          'auth_id')
        self.assertTrue(check_auth.result)
        self.assertEqual(check_auth.error_message,
                         "Authentication User has been verified")

    def test_check_wrong_uuid(self):
        run_method = ProtocolMethods('test',
                                   database=self.db)
        check_auth = run_method._check_auth('987654',
                                          'auth_id')
        self.assertFalse(check_auth.result)
        self.assertEqual(check_auth.error_message,
                         "User wasn't found in the database")

    def test_check_wrong_auth_id(self):
        run_method = ProtocolMethods('test',
                                   database=self.db)
        check_auth = run_method._check_auth('123456',
                                          'wrong_auth_id')
        self.assertFalse(check_auth.result)
        self.assertEqual(check_auth.error_message,
                         "Authentication User failed")


class TestCheckLogin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()
        cls.db = DBHandler(uri="sqlite:/:memory:")

    def setUp(self):
        self.db.create()
        self.db.add_user(uuid="123456",
                         login="login",
                         password="password",
                         auth_id="auth_id")
        self.test = api.Request.parse_file(REGISTER_USER)

    def tearDown(self):
        self.db.delete()
        del self.test

    def test_check_found_login(self):
        run_method = ProtocolMethods('test',
                                     self.db)
        result = run_method._check_login("login")
        self.assertTrue(result)

    def test_check_wrong_login(self):
        run_method = ProtocolMethods('test',
                                     self.db)
        result = run_method._check_login("wrong_login")
        self.assertFalse(result)


class TestRegisterUser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()
        cls.db = DBHandler(uri="sqlite:/:memory:")

    def setUp(self):
        self.db.create()
        self.test = api.Request.parse_file(REGISTER_USER)

    def tearDown(self):
        self.db.delete()
        del self.test

    def test_user_created(self):
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Created")

    def test_user_already_exists(self):
        self.db.add_user(uuid="123456",
                         login="login",
                         password="password")
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Conflict")

    def test_user_write_in_database(self):
        ProtocolMethods(self.test,
                        self.db)
        dbquery = self.db.get_user_by_login(login="login")
        self.assertEqual(dbquery.login, "login")

    def test_uuid_write_in_database(self):
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        dbquery = self.db.get_user_by_login("login")
        self.assertEqual(dbquery.uuid,
                         result["data"]["user"][0]["uuid"])

    def test_auth_id_write_in_database(self):
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        dbquery = self.db.get_user_by_login("login")
        self.assertEqual(dbquery.authId,
                         result["data"]["user"][0]["auth_id"])

    def test_type_of_salt(self):
        ProtocolMethods(self.test,
                        self.db)
        dbquery = self.db.get_user_by_login("login")
        self.assertIsInstance(dbquery.salt, bytes)

    def test_type_of_key(self):
        ProtocolMethods(self.test,
                        self.db)
        dbquery = self.db.get_user_by_login("login")
        self.assertIsInstance(dbquery.key, bytes)


class TestGetUpdate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()
        cls.db = DBHandler(uri="sqlite:/:memory:")

    def setUp(self):
        self.db.create()
        self.db.add_user(uuid="123456",
                         login="login",
                         password="password",
                         auth_id="auth_id")
        self.db.add_user(uuid="987654",
                         login="login2",
                         password="password2",
                         auth_id="auth_id2")
        self.db.add_user(uuid="666555",
                         login="login3",
                         password="password3",
                         auth_id="auth_id3")
        self.db.add_flow(uuid="07d949",
                         users=["123456",
                                "987654"],
                         time_created=111,
                         flow_type="chat",
                         title="title1",
                         info="info1",
                         owner="123456")
        self.db.add_flow(uuid="07d950",
                         users=["987654",
                                "987654",
                                "666555"],
                         time_created=222,
                         flow_type="group",
                         title="title2",
                         info="info2",
                         owner="987654")
        self.db.add_message(flow_uuid="07d949",
                            user_uuid="123456",
                            message_uuid="111",
                            text="Hello1",
                            time=111)
        self.db.add_message(flow_uuid="07d949",
                            user_uuid="987654",
                            message_uuid="112",
                            text="Hello2",
                            time=222)
        self.db.add_message(flow_uuid="07d950",
                            user_uuid="123456",
                            message_uuid="113",
                            text="Heeeello1",
                            time=111)
        self.db.add_message(flow_uuid="07d950",
                            user_uuid="987654",
                            message_uuid="114",
                            text="Heeeello2",
                            time=222)
        self.db.add_message(flow_uuid="07d950",
                            user_uuid="666555",
                            message_uuid="115",
                            text="Heeeello3",
                            time=333)
        self.test = api.Request.parse_file(GET_UPDATE)

    def tearDown(self):
        self.db.delete()
        del self.test

    def test_update(self):
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "OK")

    def test_check_message_in_result(self):
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["data"]["message"][1]["uuid"],
                         "112")

    def test_check_flow_in_result(self):
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["data"]["flow"][0]["owner"],
                         "123456")

    def test_check_user_in_result(self):
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["data"]["user"][2]["uuid"],
                         "666555")

    @unittest.skip("Не работает, пока не будет добавлен фильтр по времени")
    def test_no_new_data_in_database(self):
        self.test.data.time = 444
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Not Found")


class TestSendMessage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()
        cls.db = DBHandler(uri="sqlite:/:memory:")

    def setUp(self):
        self.db.create()
        self.db.add_user(uuid="123456",
                         login="login",
                         password="password",
                         auth_id="auth_id")
        self.db.add_flow(uuid="07d949",
                         users=["123456"],
                         time_created=111,
                         flow_type="group",
                         owner="123456")
        self.test = api.Request.parse_file(SEND_MESSAGE)

    def tearDown(self):
        self.db.delete()
        del self.test

    def test_send_message(self):
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "OK")

    def test_check_id_in_response(self):
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        dbquery = self.db.get_message_by_uuid("999666")
        self.assertEqual(result["data"]["message"][0]["uuid"],
                         dbquery.uuid)

    def test_check_client_id_in_response(self):
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["data"]["message"][0]["client_id"],
                         123)

    def test_wrong_flow(self):
        self.test.data.flow[0].uuid = "666666"
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Not Found")

    def test_write_text_in_database(self):
        ProtocolMethods(self.test,
                        self.db)
        dbquery = self.db.get_message_by_uuid("999666")
        self.assertEqual(dbquery.text,
                         self.test.data.message[0].text)

    def test_write_time_in_database(self):
        ProtocolMethods(self.test,
                        self.db)
        dbquery = self.db.get_message_by_uuid("999666")
        self.assertIsInstance(dbquery.time, int)


class TestAllMessages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()
        cls.db = DBHandler(uri="sqlite:/:memory:")

    def setUp(self):
        self.db.create()
        self.db.add_user(uuid="123456",
                         login="login",
                         password="password",
                         auth_id="auth_id")
        self.db.add_user(uuid="654321",
                         login="login2",
                         password="password2",
                         auth_id="auth_id2")
        self.db.add_flow(uuid="07d949",
                         users=["123456",
                                "654321"],
                         flow_type="chat",
                         owner="123456")
        self.db.add_flow(uuid="07d950",
                         users=["123456",
                                "654321"],
                         flow_type="chat",
                         owner="654321")
        for item in range(limit.getint("messages") + 10):
            self.db.add_message(flow_uuid="07d949",
                                user_uuid="123456",
                                message_uuid=str(uuid4().int),
                                text=f"Hello{item}",
                                time=item)
        for item in range(limit.getint("messages") - 10):
            self.db.add_message(flow_uuid="07d950",
                                user_uuid="654321",
                                message_uuid=str(uuid4().int),
                                text=f"Kak Dela{item}",
                                time=item)
        self.db.add_message(flow_uuid="07d950",
                            user_uuid="654321",
                            message_uuid='2715207240631768797',
                            text="Privet",
                            time=666)
        self.test = api.Request.parse_file(ALL_MESSAGES)

    def tearDown(self):
        self.db.delete()
        del self.test

    def test_all_message_fields_filled(self):
        self.test.data.flow[0].uuid = "07d950"
        check_uuid = '2715207240631768797'
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        message_found = False
        for _, item in enumerate(result["data"]["message"]):
            if item["time"] == 666:
                message_found = True
                self.assertEqual(item["uuid"], check_uuid)
                self.assertEqual(item["text"], 'Privet')
                self.assertEqual(item["from_user"], '654321')
                self.assertEqual(item["from_flow"], '07d950')
        self.assertTrue(message_found)

    def test_all_message_more_limit(self):
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Partial Content")

    def test_all_message_less_limit(self):
        self.test.data.flow[0].uuid = "07d950"
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "OK")

    def test_message_end_in_response(self):
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["data"]["flow"][0]["message_end"], 108)

    def test_message_start_in_response(self):
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["data"]["flow"][0]["message_start"], 0)

    def test_check_message_in_database(self):
        ProtocolMethods(self.test,
                        self.db)
        dbquery = self.db.get_message_by_exact_time(666)
        self.assertEqual(dbquery.text, "Privet")

    def test_wrong_message_volume(self):
        self.test.data.flow[0].message_end = 256
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Forbidden")

    def test_wrong_flow_id(self):
        self.test.data.flow[0].uuid = "666666"
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Not Found")


class TestAddFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()
        cls.db = DBHandler(uri="sqlite:/:memory:")

    def setUp(self):
        self.db.create()
        self.db.add_user(uuid="123456",
                         login="login",
                         password="password",
                         auth_id="auth_id")
        self.db.add_flow(uuid="07d949",
                         users=["123456"])
        logger.remove()
        self.test = api.Request.parse_file(ADD_FLOW)

    def tearDown(self):
        self.db.delete()
        del self.test

    def test_add_flow_group(self):
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "OK")

    def test_add_flow_channel(self):
        self.test.data.flow[0].type = "channel"
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "OK")

    def test_add_flow_bad_type(self):
        error = "Wrong flow type"
        self.test.data.flow[0].type = "unknown"
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["detail"], error)

    def test_add_flow_chat_single_user(self):
        error = "Must be two users only"
        self.test.data.flow[0].type = "chat"
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["detail"], error)

    def test_add_flow_chat_more_users(self):
        self.test.data.flow[0].type = "chat"
        self.test.data.flow[0].users.extend(["666555", "888999"])
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Bad Request")

    def test_check_flow_in_database(self):
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        dbquery = self.db.get_flow_by_title("title")
        self.assertEqual(dbquery[0].uuid,
                         result["data"]["flow"][0]["uuid"])


class TestAllFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()
        cls.db = DBHandler(uri="sqlite:/:memory:")

    def setUp(self):
        self.db.create()
        self.db.add_user(uuid="123456",
                         login="login",
                         password="password",
                         auth_id="auth_id")
        self.test = api.Request.parse_file(ALL_FLOW)

    def tearDown(self):
        self.db.delete()
        del self.test

    def test_all_flow(self):
        self.db.add_flow(uuid="07d949",
                         users=["123456"],
                         time_created=123456,
                         flow_type="group",
                         title="title",
                         info="info",
                         owner="123456")
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["data"]["flow"][0]["info"], "info")

    def test_blank_flow_table_in_database(self):
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Not Found")


class TestUserInfo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()
        cls.db = DBHandler(uri="sqlite:/:memory:")

    def setUp(self):
        self.db.create()
        for item in range(5):
            uuid = str(123456 + item)
            self.db.add_user(uuid=uuid,
                             login="login",
                             password="password",
                             username="username",
                             is_bot=False,
                             auth_id="auth_id",
                             email="email@email.com",
                             bio="bio")
        self.test = api.Request.parse_file(USER_INFO)

    def tearDown(self):
        self.db.delete()
        del self.test

    def test_user_info(self):
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "OK")

    def test_check_user_info(self):
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["data"]["user"][0]["bio"], "bio")

    def test_check_many_user_info(self):
        users = [{'uuid': str(123456 + item)} for item in range(120)]
        self.test.data.user.extend(users)
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Forbidden")


class TestAuthentification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()
        cls.db = DBHandler(uri="sqlite:/:memory:")

    def setUp(self):
        gen_hash = lib.Hash("password", 123456,
                            b"salt", b"key")
        self.hash_password = gen_hash.password_hash()
        self.db.create()
        self.db.add_user(uuid="123456",
                         login="login",
                         password="password",
                         hash_password=self.hash_password,
                         salt=b"salt",
                         key=b"key")
        self.test = api.Request.parse_file(AUTH)

    def tearDown(self):
        self.db.delete()
        del self.test

    def test_authentification(self):
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "OK")

    def test_blank_database(self):
        login = self.test.data.user[0].login
        dbquery = self.db.get_user_by_login(login)
        dbquery.delete(dbquery.id)
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Not Found")

    def test_two_element_in_database(self):
        self.db.add_user(uuid="654321",
                         login="login",
                         password="password",
                         salt=b"salt",
                         key=b"key")
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Not Found")

    def test_wrong_password(self):
        self.test.data.user[0].password = "wrong_password"
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Unauthorized")

    def test_write_in_database(self):
        login = self.test.data.user[0].login
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        dbquery = self.db.get_user_by_login(login)
        self.assertEqual(dbquery.authId,
                         result["data"]["user"][0]["auth_id"])


class TestDeleteUser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()
        cls.db = DBHandler(uri="sqlite:/:memory:")

    def setUp(self):
        self.db.create()
        self.db.add_user(uuid="123456",
                         login="login",
                         password="password",
                         auth_id="auth_id")
        self.test = api.Request.parse_file(DELETE_USER)

    def tearDown(self):
        self.db.delete()
        del self.test

    def test_delete_user(self):
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "OK")

    def test_wrong_login(self):
        self.test.data.user[0].login = "wrong_login"
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Not Found")

    def test_wrong_password(self):
        self.test.data.user[0].password = "wrong_password"
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Not Found")


class TestDeleteMessage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()
        cls.db = DBHandler(uri="sqlite:/:memory:")

    def setUp(self):
        self.db.create()
        self.db.add_user(uuid="123456",
                         login="login",
                         password="password",
                         auth_id="auth_id")
        self.db.add_flow(uuid="07d949",
                         users=["123456"],
                         time_created=111,
                         flow_type="group",
                         title="group",
                         owner="123456")
        self.db.add_message(flow_uuid="07d949",
                            user_uuid="123456",
                            message_uuid="1122",
                            text="Hello",
                            time=123456)
        self.test = api.Request.parse_file(DELETE_MESSAGE)
        logger.remove()

    def tearDown(self):
        self.db.delete()
        del self.test

    def test_delete_message(self):
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "OK")

    def test_check_delete_message_in_database(self):
        ProtocolMethods(self.test,
                        self.db)
        dbquery = self.db.get_message_by_text("Hello")
        self.assertEqual(dbquery.count(), 0)

    def test_check_deleted_message_in_database(self):
        ProtocolMethods(self.test,
                        self.db)
        dbquery = self.db.get_message_by_text("Message deleted")
        self.assertEqual(dbquery.count(), 1)

    def test_wrong_message_id(self):
        self.test.data.message[0].uuid = "2"
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Not Found")


class TestEditedMessage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()
        cls.db = DBHandler(uri="sqlite:/:memory:")

    def setUp(self):
        self.db.create()
        self.db.add_user(uuid="123456",
                         login="login",
                         password="password",
                         auth_id="auth_id")
        self.db.add_flow(uuid="07d949",
                         users=["123456"],
                         time_created=112,
                         flow_type="group",
                         title="group",
                         owner="123456")
        self.db.add_message(flow_uuid="07d949",
                            user_uuid="123456",
                            message_uuid="1",
                            text="Hello",
                            time=123456)
        self.test = api.Request.parse_file(EDITED_MESSAGE)

    def tearDown(self):
        self.db.delete()
        del self.test

    def test_edited_message(self):
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "OK")

    def test_new_edited_message(self):
        ProtocolMethods(self.test,
                        self.db)
        dbquery = self.db.get_message_by_uuid("1")
        self.assertEqual(dbquery.text, "New_Hello")

    def test_wrong_message_id(self):
        self.test.data.message[0].uuid = "3"
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Not Found")


class TestPingPong(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()
        cls.db = DBHandler(uri="sqlite:/:memory:")

    def setUp(self):
        self.db.create()
        self.db.add_user(uuid="123456",
                         login="login",
                         password="password",
                         auth_id="auth_id")
        self.test = api.Request.parse_file(PING_PONG)

    def tearDown(self):
        self.db.delete()
        del self.test

    def test_ping_pong(self):
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "OK")


class TestErrors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()
        cls.db = DBHandler(uri="sqlite:/:memory:")

    def setUp(self):
        self.db.create()
        self.db.add_user(uuid="123456",
                         login="login",
                         password="password",
                         auth_id="auth_id")

    def tearDown(self):
        self.db.delete()
        del self.test

    def test_wrong_type(self):
        self.test = api.Request.parse_file(ERRORS)
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Method Not Allowed")

    def test_unsupported_media_type(self):
        self.test = json.dumps(NON_VALID_ERRORS)
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Unsupported Media Type")

    def test_only_type_in_request(self):
        self.test = json.dumps(ERRORS_ONLY_TYPE)
        run_method = ProtocolMethods(self.test,
                                     self.db)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Unsupported Media Type")

    def test_wrong_status_in_catching_error(self):
        result = self.test.catching_error(status='err')
        self.assertEqual(result.code, 520)
        self.assertEqual(result.status, "Unknown Error")
        self.assertIsInstance(result.time, int)
        self.assertIsInstance(result.detail, str)

    def test_correct_status_in_catching_error(self):
        result = self.test.catching_error(status='BAD_REQUEST')
        self.assertEqual(result.code, 400)
        self.assertEqual(result.status, "Bad Request")
        self.assertIsInstance(result.time, int)
        self.assertIsInstance(result.detail, str)


if __name__ == "__main__":
    unittest.main()
