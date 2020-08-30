import inspect
import os
import sys
import unittest
from loguru import logger

import sqlobject as orm

# Add path to directory with code being checked
# to variable 'PATH' to import modules from directory
# above the directory with the tests.
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
FIXTURES_PATH = os.path.join(BASE_PATH, "fixtures")
VALID_JSON = os.path.join(FIXTURES_PATH, "api.json")
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
REGISTER_USER = {
    "type": "register_user",
    "data": {
        "user": {
            "password": "password",
            "login": "login",
            "email": "querty@querty.com",
            "username": "username"
            },
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
        "user": {
            "password": "password",
            "login": "login"
            },
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
        "user": {
            "uuid": 123456,
            "password": "password",
            "login": "login",
            "auth_id": "auth_id"
            },
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
        "message": {
            "id": 1,
            "time": 1594492370
            },
        "user": {
            "uuid": 123456,
            "auth_id": "auth_id"
            },
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
        "message": {
            "id": 1,
            "text": "Hello",
            "time": 1594492370
            },
        "user": {
            "uuid": 123456,
            "auth_id": "auth_id"
            },
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
        "user": {
            "uuid": 123456,
            "auth_id": "auth_id"
            },
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
        "user": {
            "uuid": 123456,
            "auth_id": "auth_id"
            },
        "meta": None
        },
    "jsonapi": {
        "version": "1.0"
        },
    "meta": None
    }

GET_UPDATE = {
    "type": "get_update",
    "data": {
        "time": 1594492370,
        "flow": {
            "id": 1
            },
        "user": {
            "uuid": 123456,
            "auth_id": "auth_id"
            },
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
        "flow": {
            "id": 123,
            "time": 1594492370,
            "type": "chat"
            },
        "message": {
            "id": 858585,
            "text": "Hello!",
            "from_user": {
                "uuid": 123456,
                "username": "username"
                },
            "time": 1594492370,
            "from_flow": {
                "id": 5656565656,
                "type": "chat"
                },
            "file": {
                "picture": "jkfikdkdsd",
                "video": "sdfsdfsdf",
                "audio": "fgfsdfsdfsdf",
                "document": "adgdfhfgth"
                },
            "emoji": "sfdfsdfsdf",
            "edited_message": {
                "time": 1594492370,
                "status": True
                },
            "reply_to": None
            },
        "user": {
            "uuid": 123456,
            "auth_id": "auth_id",
            },
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
        "user": {
            "uuid": 123456,
            "auth_id": "auth_id"
            },
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
        "user": {
            "uuid": 123456,
            "auth_id": "auth_id"
            },
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
        "user": {
            "uuid": 123456,
            "auth_id": "auth_id"
            },
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
        "flow": {
            "type": "chat",
            "title": "title",
            "info": "info"
            },
        "user": {
            "uuid": 123456,
            "auth_id": "auth_id",
            },
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


class TestCheckUuidAndAuthId(unittest.TestCase):
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
        self.uuid = 123456
        self.auth_id = "auth_id"

    def tearDown(self):
        del self.uuid
        del self.auth_id

    @classmethod
    def tearDownClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)

    def test_check_good(self):
        result = controller.check_uuid_and_auth_id(self.uuid,
                                                   self.auth_id)
        self.assertTrue(result)

    def test_check_wrong_uuid(self):
        self.uuid = 654321
        result = controller.check_uuid_and_auth_id(self.uuid,
                                                   self.auth_id)
        self.assertFalse(result)

    def test_check_wrong_auth_id(self):
        self.auth_id = "wrong_auth_id"
        result = controller.check_uuid_and_auth_id(self.uuid,
                                                   self.auth_id)
        self.assertFalse(result)


class TestServeRequest(unittest.TestCase):
    def setUp(self):
        self.valid = api.ValidJSON.parse_file(VALID_JSON)
        logger.remove()

    def tearDown(self):
        del self.valid

    def test_type_dict(self):
        result = controller.serve_request(self.valid)
        self.assertIsInstance(result, dict)

    def test_validation_error(self):
        self.valid.type = None
        result = controller.serve_request(self.valid)
        self.assertEqual(result["errors"]["code"], 520)


# TestSuite for testing protocol methods
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
        self.valid = api.ValidJSON.parse_obj(REGISTER_USER)

    def tearDown(self):
        del self.valid

    @classmethod
    def tearDownClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)

    def test_user_created(self):
        self.valid.data.user.login = "other_login"
        result = controller.register_user(self.valid)
        self.assertEqual(result["errors"]["code"], 201)

    def test_bad_request(self):
        result = controller.register_user(self.valid)
        self.assertEqual(result["errors"]["code"], 400)


class TestGetUpdate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        new_user = models.User(uuid=123456,
                               login="login",
                               password="password",
                               authId="auth_id")
        new_flow = models.Flow(flowId=1,
                               timeCreated=1,
                               flowType='chat',
                               title='title',
                               info='info')
        models.Flow(flowId=111)
        models.Message(text="Hello",
                       time=1,
                       user=new_user,
                       flow=new_flow)
        models.Message(text="Hello2",
                       time=2,
                       user=new_user,
                       flow=new_flow)
        models.Message(text="Hello3",
                       time=3,
                       user=new_user,
                       flow=new_flow)
        logger.remove()

    def setUp(self):
        self.valid = api.ValidJSON.parse_obj(GET_UPDATE)

    def tearDown(self):
        del self.valid

    @classmethod
    def tearDownClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)

    def test_wrong_uuid(self):
        self.valid.data.user.uuid = 654321
        result = controller.get_update(self.valid)
        self.assertEqual(result["errors"]["code"], 401)

    def test_wrong_auth_id(self):
        self.valid.data.user.auth_id = "wrong_auth_id"
        result = controller.get_update(self.valid)
        self.assertEqual(result["errors"]["code"], 401)

    def test_update(self):
        result = controller.get_update(self.valid)
        self.assertEqual(result["errors"]["code"], 200)

    def test_wrong_flow_id(self):
        self.valid.data.flow.id = 321
        result = controller.get_update(self.valid)
        self.assertEqual(result["errors"]["code"], 404)

    def test_no_message_in_database(self):
        self.valid.data.flow.id = 111
        result = controller.get_update(self.valid)
        self.assertEqual(result["errors"]["code"], 404)


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
        logger.remove()

    def setUp(self):
        self.valid = api.ValidJSON.parse_obj(SEND_MESSAGE)

    def tearDown(self):
        del self.valid

    @classmethod
    def tearDownClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)

    def test_send_message(self):
        result = controller.send_message(self.valid)
        self.assertEqual(result["errors"]["code"], 200)

    def test_wrong_uuid(self):
        self.valid.data.user.uuid = 654321
        result = controller.send_message(self.valid)
        self.assertEqual(result["errors"]["code"], 401)

    def test_wrong_auth_id(self):
        self.valid.data.user.auth_id = "wrong_auth_id"
        result = controller.send_message(self.valid)
        self.assertEqual(result["errors"]["code"], 401)


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
        self.valid = api.ValidJSON.parse_obj(ADD_FLOW)

    def tearDown(self):
        del self.valid

    @classmethod
    def tearDownClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)

    def test_add_flow(self):
        result = controller.add_flow(self.valid)
        self.assertEqual(result["errors"]["code"], 200)

    def test_wrong_uuid(self):
        self.valid.data.user.uuid = 654321
        result = controller.add_flow(self.valid)
        self.assertEqual(result["errors"]["code"], 401)

    def test_wrong_auth_id(self):
        self.valid.data.user.auth_id = "wrong_auth_id"
        result = controller.add_flow(self.valid)
        self.assertEqual(result["errors"]["code"], 401)


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
        models.Flow(flowId=2,
                    timeCreated=654321,
                    flowType="flow_type2",
                    title="title2",
                    info="info2")
        logger.remove()

    def setUp(self):
        self.valid = api.ValidJSON.parse_obj(ALL_FLOW)

    def tearDown(self):
        del self.valid

    @classmethod
    def tearDownClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)

    def test_all_flow(self):
        result = controller.all_flow(self.valid)
        self.assertEqual(result["errors"]["code"], 200)

    def test_wrong_uuid(self):
        self.valid.data.user.uuid = 654321
        result = controller.all_flow(self.valid)
        self.assertEqual(result["errors"]["code"], 401)

    def test_wrong_auth_id(self):
        self.valid.data.user.auth_id = "wrong_auth_id"
        result = controller.all_flow(self.valid)
        self.assertEqual(result["errors"]["code"], 401)


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
        self.dbquery = models.User.select(models.User.q.uuid ==
                                          123456)
        self.dbquery[0].authId = "auth_id"
        self.valid = api.ValidJSON.parse_obj(USER_INFO)

    def tearDown(self):
        del self.valid

    @classmethod
    def tearDownClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)

    def test_user_info(self):
        result = controller.user_info(self.valid)
        self.assertEqual(result["errors"]["code"], 200)

    def test_wrong_uuid(self):
        self.valid.data.user.uuid = 654321
        result = controller.user_info(self.valid)
        self.assertEqual(result["errors"]["code"], 401)

    def test_wrong_auth_id(self):
        self.valid.data.user.auth_id = "wrong_auth_id"
        result = controller.user_info(self.valid)
        self.assertEqual(result["errors"]["code"], 401)


class TestAuthentification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        models.User(uuid=123456,
                    login="login",
                    password="password",
                    salt="salt",
                    key="key")

    def setUp(self):
        self.valid = api.ValidJSON.parse_obj(AUTH)

    def tearDown(self):
        del self.valid

    @classmethod
    def tearDownClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)

    def test_authentification(self):
        result = controller.authentification(self.valid)
        self.assertEqual(result["errors"]["code"], 200)

    def test_wrong_login(self):
        self.valid.data.user.login = "wrong_login"
        result = controller.authentification(self.valid)
        self.assertEqual(result["errors"]["code"], 404)

    def test_wrong_password(self):
        self.valid.data.user.password = "wrong_password"
        result = controller.authentification(self.valid)
        self.assertEqual(result["errors"]["code"], 404)


class TestDeleteUser(unittest.TestCase):
    def setUp(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        models.User(uuid=123456,
                    login="login",
                    password="password",
                    authId="auth_id")
        self.valid = api.ValidJSON.parse_obj(DELETE_USER)

    def tearDown(self):
        del self.valid
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)

    def test_delete_user(self):
        result = controller.delete_user(self.valid)
        self.assertEqual(result["errors"]["code"], 200)

    def test_wrong_uuid(self):
        self.valid.data.user.uuid = 654321
        result = controller.delete_user(self.valid)
        self.assertEqual(result["errors"]["code"], 401)

    def test_wrong_auth_id(self):
        self.valid.data.user.auth_id = "wrong_auth_id"
        result = controller.delete_user(self.valid)
        self.assertEqual(result["errors"]["code"], 401)

    def test_wrong_login(self):
        self.valid.data.user.login = "wrong_login"
        result = controller.delete_user(self.valid)
        self.assertEqual(result["errors"]["code"], 404)

    def test_wrong_password(self):
        self.valid.data.user.password = "wrong_password"
        result = controller.delete_user(self.valid)
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
        self.valid = api.ValidJSON.parse_obj(DELETE_MESSAGE)

    def tearDown(self):
        del self.valid
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)

    def test_delete_message(self):
        result = controller.delete_message(self.valid)
        self.assertEqual(result["errors"]["code"], 200)

    def test_wrong_uuid(self):
        self.valid.data.user.uuid = 654321
        result = controller.delete_message(self.valid)
        self.assertEqual(result["errors"]["code"], 401)

    def test_wrong_auth_id(self):
        self.valid.data.user.auth_id = "wrong_auth_id"
        result = controller.delete_message(self.valid)
        self.assertEqual(result["errors"]["code"], 401)

    def test_wrong_message_id(self):
        self.valid.data.message.id = 2
        result = controller.delete_message(self.valid)
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
        models.Message(text="Hello",
                       time=123456,
                       user=new_user,
                       flow=new_flow)

    def setUp(self):
        self.valid = api.ValidJSON.parse_obj(EDITED_MESSAGE)

    def tearDown(self):
        del self.valid

    @classmethod
    def tearDownClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)

    def test_edited_message(self):
        result = controller.edited_message(self.valid)
        self.assertEqual(result["errors"]["code"], 200)

    def test_wrong_uuid(self):
        self.valid.data.user.uuid = 654321
        result = controller.edited_message(self.valid)
        self.assertEqual(result["errors"]["code"], 401)

    def test_wrong_auth_id(self):
        self.valid.data.user.auth_id = "wrong_auth_id"
        result = controller.edited_message(self.valid)
        self.assertEqual(result["errors"]["code"], 401)

    def test_wrong_message_id(self):
        self.valid.data.message.id = 3
        result = controller.edited_message(self.valid)
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

    def setUp(self):
        self.valid = api.ValidJSON.parse_obj(ALL_MESSAGES)

    def tearDown(self):
        del self.valid

    @classmethod
    def tearDownClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)

    def test_all_message(self):
        result = controller.all_messages(self.valid)
        self.assertEqual(result["errors"]["code"], 200)

    def test_wrong_uuid(self):
        self.valid.data.user.uuid = 654321
        result = controller.all_messages(self.valid)
        self.assertEqual(result["errors"]["code"], 401)

    def test_wrong_auth_id(self):
        self.valid.data.user.auth_id = "wrong_auth_id"
        result = controller.all_messages(self.valid)
        self.assertEqual(result["errors"]["code"], 401)

    def test_wrong_message_id(self):
        self.dbquery = models.Message.select()
        while self.dbquery.count() > 0:
            number = self.dbquery.count() - 1
            self.dbquery[number].delete(self.dbquery[number].id)
        result = controller.all_messages(self.valid)
        self.assertEqual(result["errors"]["code"], 404)

    def test_check_message_in_dict(self):
        result = controller.all_messages(self.valid)
        self.assertEqual(result["data"]["message"][3]["time"], 3)


class TestPingPong(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)

    def setUp(self):
        self.valid = api.ValidJSON.parse_obj(PING_PONG)

    def tearDown(self):
        del self.valid

    @classmethod
    def tearDownClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)

    def test_ping_pong(self):
        result = controller.ping_pong(self.valid)
        self.assertEqual(result["errors"]["code"], 200)


class TestErrors(unittest.TestCase):
    def setUp(self):
        self.valid = api.ValidJSON.parse_obj(ERRORS)

    def tearDown(self):
        del self.valid

    def test_errors(self):
        result = controller.errors(self.valid)
        self.assertEqual(result["errors"]["code"], 405)


@unittest.skip("Пример оптимизации тестов")
class TestApiControllers(unittest.TestCase):
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

    def setUp(self):
        logger.remove()

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True)

    def test_response_type_test(self):
        """[summary]
        """
        for i in testing:
            with self.subTest(i=i):
                self.valid = api.ValidJSON.parse_obj(i[1])
                methods = i[0]
                result = methods(self.valid)
                self.assertEqual(result["errors"]["code"], 200)


if __name__ == "__main__":
    unittest.main()
