"""
    Copyright (c) 2020 - present NekrodNIK, Stepan Skriabin, rus-ai and other.
    Look at the file AUTHORS.md(located at the root of the project) to get the full list.

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

# Add path to directory with code being checked
# to variable 'PATH' to import modules from directory
# above the directory with the tests.
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
FIXTURES_PATH = os.path.join(BASE_PATH, "fixtures")
sys.path.append(os.path.split(BASE_PATH)[0])

from mod import api  # noqa
from mod import controller  # noqa
from mod import lib  # noqa
from mod import models  # noqa

# ************** Read "config.ini" ********************
config = configparser.ConfigParser()
config.read('config.ini')
limit = config['SERVER_LIMIT']
# ************** END **********************************

connection = orm.connectionForURI("sqlite:/:memory:")
orm.sqlhub.processConnection = connection

classes = [cls_name for cls_name, cls_obj
           in inspect.getmembers(sys.modules["mod.models"])
           if inspect.isclass(cls_obj)]


# **************** Examples of requests ********************
#
#
# variables for repeating fields in queries:
user_uuid = "123456"
user_auth_id = "auth_id"
user_password = "password"
user_login = "login"
flow_uuid = "07d949"
#
#
# requests
GET_UPDATE = {
    "type": "get_update",
    "data": {
        "time": 111,
        "user": [{
            "uuid": user_uuid,
            "auth_id": user_auth_id
            }],
        "meta": None
        },
    "jsonapi": {
        "version": "1.0"
        },
    "meta": None
    }

SEND_MESSAGE = {
    "type": "send_message",
    "data": {
        "flow": [{
            "uuid": flow_uuid
            }],
        "message": [{
            "text": "Hello!",
            "client_id": 123,
            "file_picture": b"jkfikdkdsd",
            "file_video": b"sdfsdfsdf",
            "file_audio": b"fgfsdfsdfsdf",
            "file_document": b"adgdfhfgth",
            "emoji": b"sfdfsdfsdf"
            }],
        "user": [{
            "uuid": user_uuid,
            "auth_id": user_auth_id
            }],
        "meta": None
        },
    "jsonapi": {
        "version": "1.0"
        },
    "meta": None
    }

ALL_MESSAGES = {
    "type": "all_messages",
    "data": {
        "time": 2,
        "flow": [{
            "uuid": flow_uuid
            }],
        "user": [{
            "uuid": user_uuid,
            "auth_id": user_auth_id
            }],
        "meta": None
        },
    "jsonapi": {
        "version": "1.0"
        },
    "meta": None
    }

ADD_FLOW = {
    "type": "add_flow",
    "data": {
        "flow": [{
            "type": "group",
            "title": "title",
            "info": "info",
            "owner": "123456",
            "users": ["123456"]
            }],
        "user": [{
            "uuid": user_uuid,
            "auth_id": user_auth_id
            }],
        "meta": None
        },
    "jsonapi": {
        "version": "1.0"
        },
    "meta": None
    }

ALL_FLOW = {
    "type": "all_flow",
    "data": {
        "user": [{
            "uuid": user_uuid,
            "auth_id": user_auth_id
            }],
        "meta": None
        },
    "jsonapi": {
        "version": "1.0"
        },
    "meta": None
    }

USER_INFO = {
    "type": "user_info",
    "data": {
        "user": [{
            "uuid": user_uuid,
            "auth_id": user_auth_id
            },
            {
            "uuid": "123457"
            },
            {
            "uuid": "123458"
            },
            {
            "uuid": "123459"
            },
            {
            "uuid": "123460"
            }],
        "meta": None
        },
    "jsonapi": {
        "version": "1.0"
        },
    "meta": None
    }

REGISTER_USER = {
    "type": "register_user",
    "data": {
        "user": [{
            "password": user_password,
            "login": user_login,
            "email": "querty@querty.com",
            "username": "username"
            }],
        "meta": None
        },
    "jsonapi": {
        "version": "1.0"
        },
    "meta": None
    }

AUTH = {
    "type": "auth",
    "data": {
        "user": [{
            "password": user_password,
            "login": user_login
            }],
        "meta": None
        },
    "jsonapi": {
        "version": "1.0"
        },
    "meta": None
    }

DELETE_USER = {
    "type": "delete_user",
    "data": {
        "user": [{
            "uuid": user_uuid,
            "password": user_password,
            "login": user_login,
            "auth_id": user_auth_id
            }],
        "meta": None
        },
    "jsonapi": {
        "version": "1.0"
        },
    "meta": None
    }

DELETE_MESSAGE = {
    "type": "delete_message",
    "data": {
        "flow": [{
            "uuid": flow_uuid
            }],
        "message": [{
            "uuid": "1122"
            }],
        "user": [{
            "uuid": user_uuid,
            "auth_id": user_auth_id
            }],
        "meta": None
        },
    "jsonapi": {
        "version": "1.0"
        },
    "meta": None
    }

EDITED_MESSAGE = {
    "type": "edited_message",
    "data": {
        "message": [{
            "uuid": "1",
            "text": "New_Hello"
            }],
        "user": [{
            "uuid": user_uuid,
            "auth_id": user_auth_id
            }],
        "meta": None
        },
    "jsonapi": {
        "version": "1.0"
        },
    "meta": None
    }

PING_PONG = {
    "type": "ping-pong",
    "data": {
        "user": [{
            "uuid": user_uuid,
            "auth_id": user_auth_id
            }],
        "meta": None
        },
    "jsonapi": {
        "version": "1.0"
        },
    "meta": None
    }

ERRORS = {
    "type": "wrong type",
    "data": {
        "user": [{
            "uuid": user_uuid,
            "auth_id": user_auth_id
            }],
        "meta": None
        },
    "jsonapi": {
        "version": "1.0"
        },
    "meta": None
    }

NON_VALID_ERRORS = {
    "data": {
        "user": [{
            "uuid": user_uuid,
            "auth_id": user_auth_id
            }],
        "meta": None
        },
    "jsonapi": {
        "version": "1.0"
        },
    "meta": None
    }

ERRORS_ONLY_TYPE = {
    "type": "send_message"
    }

# **************** End examples of requests *****************


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
        self.test = api.ValidJSON.parse_obj(SEND_MESSAGE)
        self.error = controller.Error

    def tearDown(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)
        del self.test

    def test_check_decorator(self):
        def test_func(*args):
            _, uuid, auth_id = args
            if uuid == "123456" and auth_id == "auth_id":
                return True
            return False
        uuid = self.test.data.user[0].uuid
        auth_id = self.test.data.user[0].auth_id
        result = controller.User.check_auth(test_func)("", uuid, auth_id)
        self.assertTrue(result)

    @unittest.skip("Not work")
    def test_check_wrong_uuid(self):
        uuid = "654321"
        auth_id = self.test.data.user[0].auth_id
        result = controller.User.check_auth(lambda: True)(controller.Error, uuid, auth_id)
        self.assertFalse(result)

    @unittest.skip("Not work")
    def test_check_wrong_auth_id(self):
        auth_id = "wrong_auth_id"
        uuid = self.test.data.user[0].uuid
        result = controller.User.check_auth(lambda: True)("", uuid, auth_id)
        self.assertFalse(result)


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
        self.test = api.ValidJSON.parse_obj(REGISTER_USER)

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
        result = run_method._ProtocolMethods__check_login(login)
        self.assertTrue(result)

    def test_check_wrong_login(self):
        run_method = controller.ProtocolMethods(self.test)
        result = run_method._ProtocolMethods__check_login("wrong_login")
        self.assertFalse(result)


class TestRegisterUser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()

    def setUp(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        self.test = api.ValidJSON.parse_obj(REGISTER_USER)

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
        self.assertEqual(result["errors"]["code"], 201)

    def test_user_already_exists(self):
        models.UserConfig(uuid="123456",
                          login="login",
                          password="password")
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 409)

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
        self.test = api.ValidJSON.parse_obj(GET_UPDATE)

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
        self.assertEqual(result["errors"]["code"], 200)

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
        self.assertEqual(result["errors"]["code"], 404)


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
        self.test = api.ValidJSON.parse_obj(SEND_MESSAGE)

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
        self.assertEqual(result["errors"]["code"], 200)

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
        self.assertEqual(result["errors"]["code"], 404)

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
        self.test = api.ValidJSON.parse_obj(ALL_MESSAGES)

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
                break
        self.assertTrue(message_found)

    def test_all_message_more_limit(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 206)

    def test_all_message_less_limit(self):
        self.test.data.flow[0].uuid = "07d950"
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 200)

    def test_message_end_in_response(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["data"]["flow"][0]["message_end"], 108)

    def test_check_message_in_database(self):
        controller.ProtocolMethods(self.test)
        dbquery = models.Message.selectBy(time=666).getOne()
        self.assertEqual(dbquery.text, "Privet")

    def test_wrong_message_volume(self):
        self.test.data.flow[0].message_end = 256
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 403)

    def test_wrong_flow_id(self):
        self.test.data.flow[0].uuid = "666666"
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 404)


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
        self.test = api.ValidJSON.parse_obj(ADD_FLOW)

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
        self.assertEqual(result["errors"]["code"], 200)

    def test_add_flow_channel(self):
        self.test.data.flow[0].type = "channel"
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 200)

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
        self.assertEqual(result["errors"]["code"], 400)

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
        self.test = api.ValidJSON.parse_obj(ALL_FLOW)

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
        self.assertEqual(result["errors"]["code"], 404)


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
        self.test = api.ValidJSON.parse_obj(USER_INFO)

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
        self.assertEqual(result["errors"]["code"], 200)

    def test_check_user_info(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["data"]["user"][0]["bio"], "bio")

    def test_check_many_user_info(self):
        users = [{'uuid': str(123456 + item)} for item in range(120)]
        self.test.data.user.extend(users)
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 403)


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
        self.test = api.ValidJSON.parse_obj(AUTH)

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
        self.assertEqual(result["errors"]["code"], 200)

    def test_blank_database(self):
        login = self.test.data.user[0].login
        dbquery = models.UserConfig.selectBy(login=login).getOne()
        dbquery.delete(dbquery.id)
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 404)

    def test_two_element_in_database(self):
        models.UserConfig(uuid="654321",
                          login="login",
                          password="password",
                          salt=b"salt",
                          key=b"key")
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 404)

    def test_wrong_password(self):
        self.test.data.user[0].password = "wrong_password"
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 401)

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
        self.test = api.ValidJSON.parse_obj(DELETE_USER)
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
        self.assertEqual(result["errors"]["code"], 200)

    def test_wrong_login(self):
        self.test.data.user[0].login = "wrong_login"
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 404)

    def test_wrong_password(self):
        self.test.data.user[0].password = "wrong_password"
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 404)


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
        self.test = api.ValidJSON.parse_obj(DELETE_MESSAGE)
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
        self.assertEqual(result["errors"]["code"], 200)

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
        self.assertEqual(result["errors"]["code"], 404)


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
        self.test = api.ValidJSON.parse_obj(EDITED_MESSAGE)

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
        self.assertEqual(result["errors"]["code"], 200)

    def test_new_edited_message(self):
        controller.ProtocolMethods(self.test)
        dbquery = models.Message.selectBy(id=1).getOne()
        self.assertEqual(dbquery.text, "New_Hello")

    def test_wrong_message_id(self):
        self.test.data.message[0].uuid = "3"
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 404)


class TestPingPong(unittest.TestCase):
    def setUp(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        models.UserConfig(uuid="123456",
                          login="login",
                          password="password",
                          authId="auth_id")
        self.test = api.ValidJSON.parse_obj(PING_PONG)
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
        self.assertEqual(result["errors"]["code"], 200)


class TestErrors(unittest.TestCase):
    def setUp(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        models.UserConfig(uuid="123456",
                          login="login",
                          password="password",
                          authId="auth_id")
        logger.remove()

    def tearDown(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)
        del self.test

    def test_wrong_type(self):
        self.test = api.ValidJSON.parse_obj(ERRORS)
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 405)

    def test_unsupported_media_type(self):
        self.test = json.dumps(NON_VALID_ERRORS)
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 415)

    def test_only_type_in_request(self):
        self.test = json.dumps(ERRORS_ONLY_TYPE)
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 415)


if __name__ == "__main__":
    unittest.main()
