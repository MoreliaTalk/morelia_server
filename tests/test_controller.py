import inspect
import os
import sys
import unittest
import json
from loguru import logger

import sqlobject as orm

# Add path to directory with code being checked
# to variable 'PATH' to import modules from directory
# above the directory with the tests.
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
FIXTURES_PATH = os.path.join(BASE_PATH, "fixtures")
sys.path.append(os.path.split(BASE_PATH)[0])
from mod import api
from mod import lib
from mod import config
from mod import controller
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
            "id": 123,
            "time": 111,
            "type": "chat"
            }],
        "message": [{
            "id": 858585,
            "text": "Hello!",
            "from_user_uuid": 123456,
            "time": 1594492370,
            "from_flow_id": 5656565656,
            "file_picture": "jkfikdkdsd",
            "file_video": "sdfsdfsdf",
            "file_audio": "fgfsdfsdfsdf",
            "file_document": "adgdfhfgth",
            "emoji": "sfdfsdfsdf",
            "edited_time": 1594492370,
            "edited_status": True,
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
        "time": 1,
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
            "id": 1,
            "time": 1594492370
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
    # None valid blank value
    "type": ,
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

# end sample

testing = ((controller.edited_message, EDITED_MESSAGE),
           (controller.delete_message, DELETE_MESSAGE))


class TestCheckAuthToken(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        models.User(uuid=123456,
                    login="login",
                    password="password",
                    authId="auth_id")
        logger.remove()

    def setUp(self):
        self.test = json.dumps(GET_UPDATE)

    def tearDown(self):
        del self.test

    @classmethod
    def tearDownClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)

    def test_check_good(self):
        run_method = controller.ProtocolMethods(self.test)
        result = run_method._ProtocolMethods__check_auth_token()
        self.assertTrue(result)

    def test_check_wrong_uuid(self):
        self.test.data.user[0].uuid = 654321
        run_method = controller.ProtocolMethods(self.test)
        result = run_method._ProtocolMethods__check_auth_token()
        self.assertFalse(result)

    def test_check_wrong_auth_id(self):
        self.test.data.user[0].auth_id = "wrong_auth_id"
        run_method = controller.ProtocolMethods(self.test)
        result = run_method._ProtocolMethods__check_auth_token()
        self.assertFalse(result)


# TestSuite for testing class ProtocolMethods
class TestRegisterUser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        models.User(uuid=123456,
                    login="login",
                    password="password")
        logger.remove()

    def setUp(self):
        self.test = json.dumps(REGISTER_USER)

    def tearDown(self):
        del self.test

    @classmethod
    def tearDownClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)

    def test_user_created(self):
        self.test.data.user[0].login = "other_login"
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 201)

    def test_user_already_exists(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 409)

    def test_user_created_in_database(self):
        dbquery = models.User.select(models.User.q.login ==
                                     "other_login").getOne()
        self.assertEqual(dbquery.login, "other_login")

    def test_uuid_created_in_database(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        dbquery = models.User.select(models.User.q.login ==
                                     "other_login").getOne()
        self.assertEqual(dbquery.uuid, result["data"]["user"][0]["uuid"])

    def test_auth_id_created_in_database(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        dbquery = models.User.select(models.User.q.login ==
                                     "other_login").getOne()
        self.assertEqual(dbquery.authId,
                         result["data"]["user"][0]["auth_id"])

    def test_salt(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        dbquery = models.User.select(models.User.q.login ==
                                     "other_login").getOne()
        self.assertIsInstance(dbquery.salt, bytes)

    def test_key(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        dbquery = models.User.select(models.User.q.login ==
                                     "other_login").getOne()
        self.assertEqual(dbquery.key, bytes)


class TestGetUpdate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
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
        logger.remove()

    def setUp(self):
        self.test = json.dumps(GET_UPDATE)

    def tearDown(self):
        del self.test

    @classmethod
    def tearDownClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)

    def test_update(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 200)

    def test_no_message_in_database(self):
        self.test.data.time = 444
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["data"]["message"][0], None)

    def test_no_flow_in_database(self):
        self.test.data.time = 333
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["data"]["flow"][0], None)

    def test_no_data_in_database(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["data"], 404)


class TestSendMessage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
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
        logger.remove()

    def setUp(self):
        self.test = json.dumps(SEND_MESSAGE)

    def tearDown(self):
        del self.test

    @classmethod
    def tearDownClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)

    def test_send_message(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 200)

    def test_wrong_flow(self):
        self.test.data.flow[0].id = 666
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 404)


class TestAddFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        models.User(uuid=123456,
                    login="login",
                    password="password",
                    authId="auth_id")
        logger.remove()

    def setUp(self):
        self.test = json.dumps(ADD_FLOW)

    def tearDown(self):
        del self.test

    @classmethod
    def tearDownClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)

    def test_add_flow(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 200)

    def test_520_error(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 200)


class TestAllFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        models.User(uuid=123456,
                    login="login",
                    password="password",
                    authId="auth_id")
        models.Flow(flowId=1,
                    timeCreated=123456,
                    flowType="flow_type",
                    title="title",
                    info="info")
        logger.remove()

    def setUp(self):
        self.test = json.dumps(ALL_FLOW)

    def tearDown(self):
        del self.test

    @classmethod
    def tearDownClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)

    def test_all_flow(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 200)

    def test_blank_database(self):
        dbquery = models.Flow.select(models.Flow.q.flowId > 0).getOne()
        dbquery.delete(dbquery.id)
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 404)


class TestUserInfo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
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
        logger.remove()

    def setUp(self):
        self.test = json.dumps(USER_INFO)

    def tearDown(self):
        del self.test

    @classmethod
    def tearDownClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)

    def test_user_info(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 200)

    def test_blank_database(self):
        dbquery = models.User.select(models.User.q.uuid ==
                                     self.test.data.user[0].uuid)
        dbquery.delete(dbquery.id)
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 404)


class TestAuthentification(unittest.TestCase):
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
                    salt=b"salt",
                    key=b"key")
        self.test = json.dumps(AUTH)

    def tearDown(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)
        del self.test

    @classmethod
    def tearDownClass(cls):
        pass

    def test_authentification(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 200)

    def test_blank_database(self):
        dbquery = models.User.select(models.User.q.login ==
                                     self.test.data.user[0].login)
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

    def test_1_in_database(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        dbquery = models.User.select(models.User.q.login ==
                                     self.test.data.user[0].login).getOne()
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
        self.test = json.dumps(DELETE_USER)
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
        self.test = json.dumps(DELETE_MESSAGE)
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

    def test_wrong_message_id(self):
        self.test.data.message[0].id = 2
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 404)


class TestEditedMessage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
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
        logger.remove()

    def setUp(self):
        self.test = json.dumps(EDITED_MESSAGE)

    def tearDown(self):
        del self.test

    @classmethod
    def tearDownClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)

    def test_edited_message(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 200)

    def test_wrong_message_id(self):
        self.test.data.message.id = 3
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 404)


class TestAllMessages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
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
        logger.remove()

    def setUp(self):
        self.test = json.dumps(ALL_MESSAGES)

    def tearDown(self):
        del self.test

    @classmethod
    def tearDownClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)

    def test_all_message(self):
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 200)

    def test_wrong_flow_id(self):
        self.test.data.flow[0].id = 555
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 404)


class TestPingPong(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        models.User(uuid=123456,
                    login="login",
                    password="password",
                    authId="auth_id")
        logger.remove()

    def setUp(self):
        self.test = json.dumps(PING_PONG)

    def tearDown(self):
        del self.test

    @classmethod
    def tearDownClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)

    def test_ping_pong(self):
        run_method = controller.ProtocolMethods(self.test)
        result = run_method.get_response()
        self.assertEqual(result["errors"]["code"], 200)


class TestErrors(unittest.TestCase):
    def setUp(self):
        logger.remove()

    def tearDown(self):
        del self.test

    def test_errors(self):
        self.test = json.dumps(ERRORS)
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 405)

    def test_unknown_error(self):
        self.test = json.dumps(NON_VALID_ERRORS)
        run_method = controller.ProtocolMethods(self.test)
        result = json.loads(run_method.get_response())
        self.assertEqual(result["errors"]["code"], 520)


if __name__ == "__main__":
    unittest.main()
