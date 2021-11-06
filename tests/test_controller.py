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

import inspect
import json
import os
import sys
import unittest
import configparser
from uuid import uuid4

import sqlobject as orm
from loguru import logger

from mod import api  # noqa
from mod import controller  # noqa
from mod import lib  # noqa
from mod.db import models  # noqa
from mod.controller import User  # noqa

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

connection = orm.connectionForURI("sqlite:/:memory:")
orm.sqlhub.processConnection = connection

classes = [cls_name for cls_name, cls_obj
           in inspect.getmembers(sys.modules["mod.db.models"])
           if inspect.isclass(cls_obj)]


class TestCheckAuthToken(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()

    def setUp(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        models.UserConfig(uuid="123456",
                          login="login",
                          password="password",
                          authId="auth_id")
        self.test = api.Request.parse_file(SEND_MESSAGE)
        self.error = controller.Error
        self.response = list()

    def tearDown(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)
        del self.test

    def test_check_decorator(self):
        def test_func(*args):
            request = args[1]
            uuid = request.data.user[0].uuid
            auth_id = request.data.user[0].auth_id
            if uuid == "123456" and auth_id == "auth_id":
                return True
        result = controller.User.check_auth(test_func)("", self.test)
        self.assertTrue(result)

    def test_check_wrong_uuid(self):
        self.test.data.user[0].uuid = "654321"
        self.assertRaises(AttributeError,
                          lambda: User.check_auth(lambda: True)("", self.test))

    def test_check_wrong_auth_id(self):
        self.test.data.user[0].auth_id = "wrong_auth_id"
        self.assertRaises(AttributeError,
                          lambda: User.check_auth(lambda: True)("", self.test))


class TestCheckLogin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()

    def setUp(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        models.UserConfig(uuid="123456",
                          login="login",
                          password="password",
                          authId="auth_id")
        self.test = api.Request.parse_file(REGISTER_USER)

    def tearDown(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)
        del self.test

    def test_check_true_result(self):
        login = self.test.data.user[0].login
        run_method = controller.ProtocolMethods(self.test)
        result = run_method.check_login(login)
        self.assertTrue(result)

    def test_check_wrong_login(self):
        run_method = controller.ProtocolMethods(self.test)
        result = run_method.check_login("wrong_login")
        self.assertFalse(result)


class TestRegisterUser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()

    def setUp(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        self.test = api.Request.parse_file(REGISTER_USER)

    def tearDown(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)
        del self.test

    def test_user_created(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Created")

    def test_user_already_exists(self):
        models.UserConfig(uuid="123456",
                          login="login",
                          password="password")
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Conflict")

    def test_user_write_in_database(self):
        controller.ProtocolMethods(self.test)
        dbquery = models.UserConfig.selectBy(login="login").getOne()
        self.assertEqual(dbquery.login, "login")

    def test_uuid_write_in_database(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        dbquery = models.UserConfig.selectBy(login="login").getOne()
        self.assertEqual(dbquery.uuid,
                         result["data"]["user"][0]["uuid"])

    def test_auth_id_write_in_database(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        dbquery = models.UserConfig.selectBy(login="login").getOne()
        self.assertEqual(dbquery.authId,
                         result["data"]["user"][0]["auth_id"])

    def test_type_of_salt(self):
        controller.ProtocolMethods(self.test)
        dbquery = models.UserConfig.selectBy(login="login").getOne()
        self.assertIsInstance(dbquery.salt, bytes)

    def test_type_of_key(self):
        controller.ProtocolMethods(self.test)
        dbquery = models.UserConfig.selectBy(login="login").getOne()
        self.assertIsInstance(dbquery.key, bytes)


class TestGetUpdate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()

    def setUp(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        new_user1 = models.UserConfig(uuid="123456",
                                      login="login",
                                      password="password",
                                      authId="auth_id")
        new_user2 = models.UserConfig(uuid="987654",
                                      login="login2",
                                      password="password2",
                                      authId="auth_id2")
        new_user3 = models.UserConfig(uuid="666555",
                                      login="login3",
                                      password="password3",
                                      authId="auth_id3")
        new_flow1 = models.Flow(uuid="07d949",
                                timeCreated=111,
                                flowType="chat",
                                title="title1",
                                info="info1",
                                owner="123456")
        new_flow2 = models.Flow(uuid="07d950",
                                timeCreated=222,
                                flowType="group",
                                title="title2",
                                info="info2",
                                owner="987654")
        new_flow1.addUserConfig(new_user1)
        new_flow1.addUserConfig(new_user2)
        new_flow2.addUserConfig(new_user2)
        new_flow2.addUserConfig(new_user1)
        new_flow2.addUserConfig(new_user3)
        models.Message(uuid="111",
                       text="Hello1",
                       time=111,
                       user=new_user1,
                       flow=new_flow1)
        models.Message(uuid="112",
                       text="Hello2",
                       time=222,
                       user=new_user2,
                       flow=new_flow1)
        models.Message(uuid="113",
                       text="Heeeello1",
                       time=111,
                       user=new_user1,
                       flow=new_flow2)
        models.Message(uuid="114",
                       text="Heeeello2",
                       time=222,
                       user=new_user2,
                       flow=new_flow2)
        models.Message(uuid="115",
                       text="Heeeello3",
                       time=333,
                       user=new_user3,
                       flow=new_flow2)
        self.test = api.Request.parse_file(GET_UPDATE)

    def tearDown(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)
        del self.test

    def test_update(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "OK")

    def test_check_message_in_result(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["data"]["message"][1]["uuid"],
                         "112")

    def test_check_flow_in_result(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["data"]["flow"][0]["owner"],
                         "123456")

    def test_check_user_in_result(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["data"]["user"][2]["uuid"],
                         "666555")

    @unittest.skip("Не работает, пока не будет добавлен фильтр по времени")
    def test_no_new_data_in_database(self):
        self.test.data.time = 444
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Not Found")


class TestSendMessage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()

    def setUp(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        new_user = models.UserConfig(uuid="123456",
                                     login="login",
                                     password="password",
                                     authId="auth_id")
        new_flow = models.Flow(uuid="07d949",
                               timeCreated=111,
                               flowType="group",
                               owner="123456")
        new_flow.addUserConfig(new_user)
        self.test = api.Request.parse_file(SEND_MESSAGE)

    def tearDown(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)
        del self.test

    def test_send_message(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "OK")

    def test_check_id_in_response(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        dbquery = models.Message.selectBy().getOne()
        self.assertEqual(result["data"]["message"][0]["uuid"],
                         dbquery.uuid)

    def test_check_client_id_in_response(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["data"]["message"][0]["client_id"],
                         123)

    def test_wrong_flow(self):
        self.test.data.flow[0].uuid = "666666"
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Not Found")

    def test_write_text_in_database(self):
        controller.ProtocolMethods(self.test)
        dbquery = models.Message.selectBy().getOne()
        self.assertEqual(dbquery.text,
                         self.test.data.message[0].text)

    def test_write_time_in_database(self):
        controller.ProtocolMethods(self.test)
        dbquery = models.Message.selectBy().getOne()
        self.assertIsInstance(dbquery.time, int)


class TestAllMessages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()

    def setUp(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        new_user = models.UserConfig(uuid="123456",
                                     login="login",
                                     password="password",
                                     authId="auth_id")
        new_user2 = models.UserConfig(uuid="654321",
                                      login="login2",
                                      password="password2",
                                      authId="auth_id2")
        new_flow = models.Flow(uuid="07d949",
                               flowType="chat",
                               owner="123456")
        new_flow2 = models.Flow(uuid="07d950",
                                flowType="chat",
                                owner="654321")
        new_flow.addUserConfig(new_user)
        new_flow.addUserConfig(new_user2)
        new_flow2.addUserConfig(new_user)
        new_flow2.addUserConfig(new_user2)
        for item in range(limit.getint("messages") + 10):
            models.Message(uuid=str(uuid4().int),
                           text=f"Hello{item}",
                           time=item,
                           user=new_user,
                           flow=new_flow)
        for item in range(limit.getint("messages") - 10):
            models.Message(uuid=str(uuid4().int),
                           text=f"Kak Dela{item}",
                           time=item,
                           user=new_user2,
                           flow=new_flow2)
        models.Message(uuid='271520724063176879757028074376756118591',
                       text="Privet",
                       time=666,
                       user=new_user2,
                       flow=new_flow2)
        self.test = api.Request.parse_file(ALL_MESSAGES)

    def tearDown(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)
        del self.test

    def test_all_message_fields_filled(self):
        self.test.data.flow[0].uuid = "07d950"
        check_uuid = '271520724063176879757028074376756118591'
        run_method = controller.ProtocolMethods(self.test)
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
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Partial Content")

    def test_all_message_less_limit(self):
        self.test.data.flow[0].uuid = "07d950"
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "OK")

    def test_message_end_in_response(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["data"]["flow"][0]["message_end"], 108)

    def test_message_start_in_response(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["data"]["flow"][0]["message_start"], 0)

    def test_check_message_in_database(self):
        controller.ProtocolMethods(self.test)
        dbquery = models.Message.selectBy(time=666).getOne()
        self.assertEqual(dbquery.text, "Privet")

    def test_wrong_message_volume(self):
        self.test.data.flow[0].message_end = 256
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Forbidden")

    def test_wrong_flow_id(self):
        self.test.data.flow[0].uuid = "666666"
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Not Found")


class TestAddFlow(unittest.TestCase):
    def setUp(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        models.UserConfig(uuid="123456",
                          login="login",
                          password="password",
                          authId="auth_id")
        models.Flow(uuid="07d949")
        logger.remove()
        self.test = api.Request.parse_file(ADD_FLOW)

    def tearDown(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)
        del self.test

    def test_add_flow_group(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "OK")

    def test_add_flow_channel(self):
        self.test.data.flow[0].type = "channel"
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "OK")

    def test_add_flow_bad_type(self):
        error = "Wrong flow type"
        self.test.data.flow[0].type = "unknown"
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["detail"], error)

    def test_add_flow_chat_single_user(self):
        error = "Must be two users only"
        self.test.data.flow[0].type = "chat"
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["detail"], error)

    def test_add_flow_chat_more_users(self):
        self.test.data.flow[0].type = "chat"
        self.test.data.flow[0].users.extend(["666555", "888999"])
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Bad Request")

    def test_check_flow_in_database(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        dbquery = models.Flow.selectBy(title="title").getOne()
        self.assertEqual(dbquery.uuid,
                         result["data"]["flow"][0]["uuid"])


class TestAllFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()

    def setUp(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        models.UserConfig(uuid="123456",
                          login="login",
                          password="password",
                          authId="auth_id")
        self.test = api.Request.parse_file(ALL_FLOW)

    def tearDown(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)
        del self.test

    def test_all_flow(self):
        models.Flow(uuid="07d949",
                    timeCreated=123456,
                    flowType="group",
                    title="title",
                    info="info",
                    owner="123456")
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["data"]["flow"][0]["info"], "info")

    def test_blank_flow_table_in_database(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Not Found")


class TestUserInfo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()

    def setUp(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        for item in range(5):
            uuid = str(123456 + item)
            models.UserConfig(uuid=uuid,
                              login="login",
                              password="password",
                              username="username",
                              isBot=False,
                              authId="auth_id",
                              email="email@email.com",
                              bio="bio")
        self.test = api.Request.parse_file(USER_INFO)

    def tearDown(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)
        del self.test

    def test_user_info(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "OK")

    def test_check_user_info(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["data"]["user"][0]["bio"], "bio")

    def test_check_many_user_info(self):
        users = [{'uuid': str(123456 + item)} for item in range(120)]
        self.test.data.user.extend(users)
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Forbidden")


class TestAuthentification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()

    def setUp(self):
        gen_hash = lib.Hash("password", 123456,
                            b"salt", b"key")
        self.hash_password = gen_hash.password_hash()
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        models.UserConfig(uuid="123456",
                          login="login",
                          password="password",
                          hashPassword=self.hash_password,
                          salt=b"salt",
                          key=b"key")
        self.test = api.Request.parse_file(AUTH)

    def tearDown(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)
        del self.test

    def test_authentification(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "OK")

    def test_blank_database(self):
        login = self.test.data.user[0].login
        dbquery = models.UserConfig.selectBy(login=login).getOne()
        dbquery.delete(dbquery.id)
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Not Found")

    def test_two_element_in_database(self):
        models.UserConfig(uuid="654321",
                          login="login",
                          password="password",
                          salt=b"salt",
                          key=b"key")
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Not Found")

    def test_wrong_password(self):
        self.test.data.user[0].password = "wrong_password"
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Unauthorized")

    def test_write_in_database(self):
        login = self.test.data.user[0].login
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        dbquery = models.UserConfig.selectBy(login=login).getOne()
        self.assertEqual(dbquery.authId,
                         result["data"]["user"][0]["auth_id"])


class TestDeleteUser(unittest.TestCase):
    def setUp(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        models.UserConfig(uuid="123456",
                          login="login",
                          password="password",
                          authId="auth_id")
        self.test = api.Request.parse_file(DELETE_USER)
        logger.remove()

    def tearDown(self):
        del self.test
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)

    def test_delete_user(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "OK")

    def test_wrong_login(self):
        self.test.data.user[0].login = "wrong_login"
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Not Found")

    def test_wrong_password(self):
        self.test.data.user[0].password = "wrong_password"
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Not Found")


class TestDeleteMessage(unittest.TestCase):
    def setUp(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)

        new_user = models.UserConfig(uuid="123456",
                                     login="login",
                                     password="password",
                                     authId="auth_id")
        new_flow = models.Flow(uuid="07d949",
                               timeCreated=111,
                               flowType="group",
                               title="group",
                               owner="123456")
        new_flow.addUserConfig(new_user)
        models.Message(uuid="1122",
                       text="Hello",
                       time=123456,
                       user=new_user,
                       flow=new_flow)
        self.test = api.Request.parse_file(DELETE_MESSAGE)
        logger.remove()

    def tearDown(self):
        del self.test
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)

    def test_delete_message(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "OK")

    def test_check_delete_message_in_database(self):
        controller.ProtocolMethods(self.test)
        dbquery = models.Message.selectBy(text="Hello")
        self.assertEqual(dbquery.count(), 0)

    def test_check_deleted_message_in_database(self):
        controller.ProtocolMethods(self.test)
        dbquery = models.Message.selectBy(text="Message deleted")
        self.assertEqual(dbquery.count(), 1)

    def test_wrong_message_id(self):
        self.test.data.message[0].uuid = "2"
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Not Found")


class TestEditedMessage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()

    def setUp(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        new_user = models.UserConfig(uuid="123456",
                                     login="login",
                                     password="password",
                                     authId="auth_id")
        new_flow = models.Flow(uuid="07d949",
                               timeCreated=112,
                               flowType="group",
                               title="group",
                               owner="123456")
        new_flow.addUserConfig(new_user)
        models.Message(uuid="1",
                       text="Hello",
                       time=123456,
                       user=new_user,
                       flow=new_flow)
        self.test = api.Request.parse_file(EDITED_MESSAGE)

    def tearDown(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)
        del self.test

    def test_edited_message(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "OK")

    def test_new_edited_message(self):
        controller.ProtocolMethods(self.test)
        dbquery = models.Message.selectBy(id=1).getOne()
        self.assertEqual(dbquery.text, "New_Hello")

    def test_wrong_message_id(self):
        self.test.data.message[0].uuid = "3"
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Not Found")


class TestPingPong(unittest.TestCase):
    def setUp(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        models.UserConfig(uuid="123456",
                          login="login",
                          password="password",
                          authId="auth_id")
        self.test = api.Request.parse_file(PING_PONG)
        logger.remove()

    def tearDown(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)
        del self.test

    def test_ping_pong(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "OK")


class TestErrors(unittest.TestCase):
    def setUp(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        models.UserConfig(uuid="123456",
                          login="login",
                          password="password",
                          authId="auth_id")
        self.test = controller.Error()
        logger.remove()

    def tearDown(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)
        del self.test

    def test_wrong_type(self):
        self.test = api.Request.parse_file(ERRORS)
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Method Not Allowed")

    def test_unsupported_media_type(self):
        self.test = json.dumps(NON_VALID_ERRORS)
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["status"],
                         "Unsupported Media Type")

    def test_only_type_in_request(self):
        self.test = json.dumps(ERRORS_ONLY_TYPE)
        run_method = controller.ProtocolMethods(self.test)
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
