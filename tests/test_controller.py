import inspect
import json
import os
import sys
import unittest

import sqlobject as orm
from loguru import logger

# Add path to directory with code being checked
# to variable 'PATH' to import modules from directory
# above the directory with the tests.
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
FIXTURES_PATH = os.path.join(BASE_PATH, "fixtures")
sys.path.append(os.path.split(BASE_PATH)[0])
from mod import api
from mod import controller
from mod import lib
from mod import models

connection = orm.connectionForURI("sqlite:/:memory:")
orm.sqlhub.processConnection = connection

classes = [cls_name for cls_name, cls_obj
           in inspect.getmembers(sys.modules["mod.models"])
           if inspect.isclass(cls_obj)]


# JSON-object for test
GET_UPDATE = {
    "type": "get_update",
    "data": {
        "time": 111,
        "user": [{
            "uuid": 123456,
            "auth_id": "auth_id"
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
            "id": 123
            }],
        "message": [{
            "text": "Hello!",
            "file_picture": b"jkfikdkdsd",
            "file_video": b"sdfsdfsdf",
            "file_audio": b"fgfsdfsdfsdf",
            "file_document": b"adgdfhfgth",
            "emoji": b"sfdfsdfsdf"
            }],
        "user": [{
            "uuid": 123456,
            "auth_id": "auth_id",
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
            "id": 123
        }],
        "user": [{
            "uuid": 123456,
            "auth_id": "auth_id"
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
            "type": "chat",
            "title": "title",
            "info": "info"
            }],
        "user": [{
            "uuid": 123456,
            "auth_id": "auth_id",
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
            "uuid": 123456,
            "auth_id": "auth_id"
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
            "uuid": 123456,
            "auth_id": "auth_id"
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
            "password": "password",
            "login": "login",
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
            "password": "password",
            "login": "login"
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
            "uuid": 123456,
            "password": "password",
            "login": "login",
            "auth_id": "auth_id"
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
        "message": [{
            "id": 1
            }],
        "user": [{
            "uuid": 123456,
            "auth_id": "auth_id"
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
            "id": 1,
            "text": "New_Hello"
            }],
        "user": [{
            "uuid": 123456,
            "auth_id": "auth_id"
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
            "uuid": 123456,
            "auth_id": "auth_id"
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
            "uuid": 123456,
            "auth_id": "auth_id"
            }],
        "meta": None
        },
    "jsonapi": {
        "version": "1.0"
        },
    "meta": None
    }

NON_VALID_ERRORS = {
    # None valid blank dict
    "type": {},
    "data": {
        "user": [{
            "uuid": 123456,
            "auth_id": "auth_id"
            }],
        "meta": None
        },
    "jsonapi": {
        "version": "1.0"
        },
    "meta": None
    }

# end


class TestCheckAuthToken(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()

    def setUp(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        models.User(uuid=123456,
                    login="login",
                    password="password",
                    authId="auth_id")
        self.test = api.ValidJSON.parse_obj(SEND_MESSAGE)

    def tearDown(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)
        del self.test

    def test_check_true_result(self):
        uuid = self.test.data.user[0].uuid
        auth_id = self.test.data.user[0].auth_id
        run_method = controller.ProtocolMethods(self.test)
        result = run_method._ProtocolMethods__check_auth_token(uuid,
                                                               auth_id)
        self.assertTrue(result)

    def test_check_wrong_uuid(self):
        uuid = 654321
        auth_id = self.test.data.user[0].auth_id
        run_method = controller.ProtocolMethods(self.test)
        result = run_method._ProtocolMethods__check_auth_token(uuid,
                                                               auth_id)
        self.assertFalse(result)

    def test_check_wrong_auth_id(self):
        auth_id = "wrong_auth_id"
        uuid = self.test.data.user[0].uuid
        run_method = controller.ProtocolMethods(self.test)
        result = run_method._ProtocolMethods__check_auth_token(uuid,
                                                               auth_id)
        self.assertFalse(result)


class TestCheckLogin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()

    def setUp(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        models.User(uuid=123456,
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
        models.User(uuid=123456,
                    login="login",
                    password="password")
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 409)

    def test_user_write_in_database(self):
        controller.ProtocolMethods(self.test)
        dbquery = models.User.selectBy(login="login").getOne()
        self.assertEqual(dbquery.login, "login")

    def test_uuid_write_in_database(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        dbquery = models.User.selectBy(login="login").getOne()
        self.assertEqual(dbquery.uuid,
                         result["data"]["user"][0]["uuid"])

    def test_auth_id_write_in_database(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        dbquery = models.User.selectBy(login="login").getOne()
        self.assertEqual(dbquery.authId,
                         result["data"]["user"][0]["auth_id"])

    def test_type_of_salt(self):
        controller.ProtocolMethods(self.test)
        dbquery = models.User.selectBy(login="login").getOne()
        self.assertIsInstance(dbquery.salt, bytes)

    def test_type_of_key(self):
        controller.ProtocolMethods(self.test)
        dbquery = models.User.selectBy(login="login").getOne()
        self.assertIsInstance(dbquery.key, bytes)


class TestGetUpdate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()

    def setUp(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        new_user1 = models.User(uuid=123456,
                                login="login",
                                password="password",
                                authId="auth_id")
        new_user2 = models.User(uuid=987654,
                                login="login2",
                                password="password2",
                                authId="auth_id2")
        new_flow1 = models.Flow(flowId=1,
                                timeCreated=111,
                                flowType='chat',
                                title='title2',
                                info='info2')
        new_flow2 = models.Flow(flowId=2,
                                timeCreated=222,
                                flowType='chat',
                                title='title2',
                                info='info2')
        models.Message(text="Hello1",
                       time=111,
                       user=new_user1,
                       flow=new_flow1)
        models.Message(text="Hello2",
                       time=222,
                       user=new_user2,
                       flow=new_flow2)
        models.Message(text="Hello3",
                       time=333,
                       user=new_user1,
                       flow=new_flow1)
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
        self.assertEqual(result["data"]["message"][1]["text"],
                         "Hello2")

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
        models.User(uuid=123456,
                    login="login",
                    password="password",
                    authId="auth_id")
        models.Flow(flowId=123,
                    timeCreated=111,
                    flowType="chat")
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

    def test_wrong_flow(self):
        self.test.data.flow[0].id = 666
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 404)

    def test_write_text_in_database(self):
        flow_id = self.test.data.flow[0].id
        controller.ProtocolMethods(self.test)
        dbquery = models.Message.selectBy(flowID=flow_id).getOne()
        self.assertEqual(dbquery.text,
                         self.test.data.message[0].text)

    def test_write_time_in_database(self):
        flow_id = self.test.data.flow[0].id
        controller.ProtocolMethods(self.test)
        dbquery = models.Message.selectBy(flowID=flow_id).getOne()
        self.assertIsInstance(dbquery.time, int)


class TestAddFlow(unittest.TestCase):
    def setUp(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        models.User(uuid=123456,
                    login="login",
                    password="password",
                    authId="auth_id")
        models.Flow(flowId=333)
        logger.remove()
        self.test = api.ValidJSON.parse_obj(ADD_FLOW)

    def tearDown(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)
        del self.test

    def test_add_flow(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 200)

    def test_check_flow_in_database(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        dbquery = models.Flow.selectBy(title="title").getOne()
        self.assertEqual(dbquery.flowId,
                         result["data"]["flow"][0]["id"])


class TestAllFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()

    def setUp(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        models.User(uuid=123456,
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
        models.Flow(flowId=1,
                    timeCreated=123456,
                    flowType="flow_type",
                    title="title",
                    info="info")
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
        models.User(uuid=123456,
                    login="login",
                    password="password",
                    username="username",
                    isBot=False,
                    authId="auth_id",
                    email='email@email.com',
                    bio='bio')
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
        models.User(uuid=123456,
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
        dbquery = models.User.selectBy(login=login).getOne()
        dbquery.delete(dbquery.id)
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 404)

    def test_two_element_in_database(self):
        models.User(uuid=654321,
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
        dbquery = models.User.selectBy(login=login).getOne()
        self.assertEqual(dbquery.authId,
                         result["data"]["user"][0]["auth_id"])


class TestDeleteUser(unittest.TestCase):
    def setUp(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        models.User(uuid=123456,
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
        new_user = models.User(uuid=123456,
                               login="login",
                               password="password",
                               authId="auth_id")
        new_flow = models.Flow(flowId=123)
        models.Message(text="Hello",
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

    def test_wrong_message_id(self):
        self.test.data.message[0].id = 2
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
        new_user = models.User(uuid=123456,
                               login="login",
                               password="password",
                               authId="auth_id")
        new_flow = models.Flow(flowId=123)
        models.Message(id=1,
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
        self.test.data.message[0].id = 3
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 404)


class TestAllMessages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()

    def setUp(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        new_user = models.User(uuid=123456,
                               login="login",
                               password="password",
                               authId="auth_id")
        new_user2 = models.User(uuid=654321,
                                login="login2",
                                password="password2",
                                authId="auth_id2")
        new_flow = models.Flow(flowId=123)
        new_flow2 = models.Flow(flowId=321)
        models.Message(text="Hello",
                       time=1,
                       user=new_user,
                       flow=new_flow)
        models.Message(text="Privet",
                       time=2,
                       user=new_user,
                       flow=new_flow)
        models.Message(text="Hello2",
                       time=3,
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

    def test_all_message(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 200)

    def test_check_message_in_database(self):
        controller.ProtocolMethods(self.test)
        dbquery = models.Message.selectBy(time=3).getOne()
        self.assertEqual(dbquery.text, "Hello2")

    def test_wrong_flow_id(self):
        self.test.data.flow[0].id = 555
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 404)


class TestPingPong(unittest.TestCase):
    def setUp(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        models.User(uuid=123456,
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
        models.User(uuid=123456,
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

    def test_wrong_type_method(self):
        self.test = api.ValidJSON.parse_obj(ERRORS)
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 405)

    def test_unsupported_media_type(self):
        self.test = json.dumps(NON_VALID_ERRORS)
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 415)


if __name__ == "__main__":
    unittest.main()
