import inspect
import os
import sys
import unittest
from loguru import logger

import sqlobject as orm

BASE_PATH = os.path.abspath(os.path.dirname(__file__))
FIXTURES_PATH = os.path.join(BASE_PATH, 'fixtures')
VALID_JSON = os.path.join(FIXTURES_PATH, 'api.json')
NOT_VALID_JSON = os.path.join(FIXTURES_PATH, 'not_valid_api.json')
sys.path.append(os.path.split(BASE_PATH)[0])
from mod import api
from mod import lib
from mod import config
from mod import controller
from mod import models

connection = orm.connectionForURI('sqlite:/:memory:')
orm.sqlhub.processConnection = connection

classes = [cls_name for cls_name, cls_obj
           in inspect.getmembers(sys.modules['mod.models'])
           if inspect.isclass(cls_obj)]


testing_methods = {
    1: {
        'type': 'controller.register_user',
        'fixtures': 'REGISTER_USER'
        },
    2: {
        'type': 'controller.get_update',
        'fixtures': 'GET_UPDATE'
        }
    }

# sample
REGISTER_USER = {
    "type": "register_user",
    "data": {
        "user": {
            "password": "ds45ds45fd45fd",
            "login": "User",
            "email": "querty@querty.com",
            "username": "User1"
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
            "id": 858585,
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
            "uuid": 5345634567354,
            "auth_id": "lkds89ds89fd98fd"
            },
        "meta": None
        },
    "jsonapi": {
        "version": "1.0"
        },
    "meta": None
    }

ERRORS = {
    "data": {
        "uuid": 45654645,
        "auth_id": "asdfadsfadfggzasd"
        }
    }

GET_UPDATE = {
    "type": "get_update",
    "data": {
        "time": 1594492370,
        "flow": {
            "id": 123
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
            "uuid": 111111111,
            "auth_id": "dks7sd9f6g4fg67vb78g65"
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

ADD_FLOW = {}
# end sample


class TestCheckUuidAndAuthId(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        models.User(uuid=123456,
                    login='login',
                    password='password',
                    authId='auth_id')

    def setUp(self):
        self.uuid = 123456
        self.auth_id = 'auth_id'

    def tearDown(self):
        del self.uuid
        del self.auth_id

    @classmethod
    def tearDownClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True, dropJoinTables=True, cascade=True)

    def test_check_uuid_and_auth_id_response_true(self):
        self.assertTrue(controller.check_uuid_and_auth_id(self.uuid,
                                                          self.auth_id))

    def test_check_uuid_and_auth_id_response_false(self):
        self.uuid = 111111
        self.auth_id = 'wrong_auth_id'
        self.assertFalse(controller.check_uuid_and_auth_id(self.uuid,
                                                           self.auth_id))


@unittest.skip('FIXME')
class TestServeRequest(unittest.TestCase):
    def setUp(self):
        self.test = api.ValidJSON.parse_file(VALID_JSON)

    def tearDown(self):
        del self.test

    def test_serve_request_type_dict(self):
        self.assertIsInstance(controller.serve_request(self.test),
                              dict)

    def test_serve_request_validation_error(self):
        self.test = api.ValidJSON.parse_file(NOT_VALID_JSON)
        self.assertIsInstance(controller.serve_request(self.test),
                              dict)

    def test_serve_request_validation_error_check_code(self):
        self.test = api.ValidJSON.parse_file(NOT_VALID_JSON)
        result = controller.serve_request(self.test)
        self.assertEqual(result['errors']['code'], 520)


# TestSuite for testing protocol methods
class TestRegisterUser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)

    def setUp(self):
        self.valid = api.ValidJSON.parse_obj(REGISTER_USER)

    def tearDown(self):
        del self.valid

    @classmethod
    def tearDownClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True, dropJoinTables=True, cascade=True)

    def test_register_user_response_type(self):
        self.assertIsInstance(controller.register_user(self.valid),
                              dict)

    def test_register_user_check_code_200(self):
        result = controller.register_user(self.valid)
        self.assertEqual(result['errors']['code'], 201)

    def test_register_user_check_code_400(self):
        models.User(uuid=123456,
                    password=REGISTER_USER['data']['user']['password'],
                    login=REGISTER_USER['data']['user']['login'],
                    username=REGISTER_USER['data']['user']['username'])
        result = controller.register_user(self.valid)
        self.assertEqual(result['errors']['code'], 400)


@unittest.skip('FIXME')
class TestGetUpdate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        models.User(uuid=123456,
                    login='login',
                    password='password',
                    authId='auth_id')

    def setUp(self):
        self.valid = api.ValidJSON.parse_obj(GET_UPDATE)

    def tearDown(self):
        del self.valid

    @classmethod
    def tearDownClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True, dropJoinTables=True, cascade=True)

    def test_get_update_response_type(self):
        self.assertIsInstance(controller.get_update(self.valid),
                              dict)

    def test_get_update_check_update(self):
        models.Flow(flowId=123)
        models.Message()
        result = controller.get_update(self.valid)
        self.assertEqual(result['errors']['code'], 200)

    def test_get_update_check_not_found(self):
        models.Flow(flowId=321)
        result = controller.get_update(self.valid)
        self.assertEqual(result['errors']['code'], 404)


@unittest.skip('FIXME')
class TestSendMessage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)

    def setUp(self):
        models.User(uuid=123456,
                    login='login',
                    password='password',
                    authId='auth_id')
        self.valid = api.ValidJSON.parse_obj(SEND_MESSAGE)

    def tearDown(self):
        del self.valid
        self.dbquery = models.User.select(models.User.q.uuid == 123456)
        self.dbquery[0].delete(self.dbquery[0].id)

    @classmethod
    def tearDownClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True, dropJoinTables=True, cascade=True)

    def test_send_message_response_type(self):
        self.assertIsInstance(controller.send_message(self.valid),
                              dict)

    def test_send_message_check_code_200(self):
        result = controller.send_message(self.valid)
        self.assertEqual(result['errors']['code'], 200)

    def test_send_message_check_code_401(self):
        self.dbquery = models.User.select(models.User.q.uuid == 123456)
        self.dbquery[0].authId = 'wrong_auth_id'
        result = controller.send_message(self.valid)
        self.assertEqual(result['errors']['code'], 401)


@unittest.skip('FIXME')
class TestAddFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)

    def setUp(self):
        self.valid = api.ValidJSON.parse_obj(ADD_FLOW)

    def tearDown(self):
        del self.valid

    @classmethod
    def tearDownClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True, dropJoinTables=True, cascade=True)

    def test_add_flow_response_type(self):
        self.assertIsInstance(controller.add_flow(self.valid),
                              dict)


class TestAllFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        models.Flow(flowId=1,
                    timeCreated=123456,
                    flowType='flow_type',
                    title='title',
                    info='info')
        models.Flow(flowId=2,
                    timeCreated=654321,
                    flowType='flow_type2',
                    title='title2',
                    info='info2')

    def setUp(self):
        self.valid = api.ValidJSON.parse_obj(ALL_FLOW)

    def tearDown(self):
        del self.valid

    @classmethod
    def tearDownClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True, dropJoinTables=True, cascade=True)

    def test_all_flow_response_type(self):
        self.assertIsInstance(controller.register_user(self.valid),
                              dict)

    def test_all_flow_check_code(self):
        result = controller.all_flow(self.valid)
        self.assertEqual(result['errors']['code'], 200)


class TestUserInfo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        models.User(uuid=123456,
                    login='login',
                    password='password')
        logger.remove()

    def setUp(self):
        self.dbquery = models.User.select(models.User.q.uuid == 123456)
        self.dbquery[0].authId = 'auth_id'
        self.valid = api.ValidJSON.parse_obj(USER_INFO)

    def tearDown(self):
        del self.valid

    @classmethod
    def tearDownClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True, dropJoinTables=True, cascade=True)

    def test_user_info_response_type(self):
        self.assertIsInstance(controller.user_info(self.valid),
                              dict)

    def test_user_info_check_code_200(self):
        result = controller.user_info(self.valid)
        self.assertEqual(result['errors']['code'], 200)

    def test_user_info_check_code_401(self):
        self.dbquery[0].authId = 'wrong_auth_id'
        result = controller.user_info(self.valid)
        self.assertEqual(result['errors']['code'], 401)


class TestAuthentification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        models.User(uuid=123456,
                    login='login',
                    password='password',
                    salt='salt',
                    key='key')

    def setUp(self):
        self.valid = api.ValidJSON.parse_obj(AUTH)

    def tearDown(self):
        del self.valid

    @classmethod
    def tearDownClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True, dropJoinTables=True, cascade=True)

    def test_authentification_response_type(self):
        self.assertIsInstance(controller.authentification(self.valid),
                              dict)

    def test_authentification_check_code_200(self):
        result = controller.authentification(self.valid)
        self.assertEqual(result['errors']['code'], 200)

    def test_authentification_check_code_404(self):
        self.dbquery = models.User.select(models.User.q.uuid == 123456)
        self.dbquery[0].login = 'wrong_login'
        result = controller.authentification(self.valid)
        self.assertEqual(result['errors']['code'], 404)


@unittest.skip('FIXME')
class TestDeleteUser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        models.User(uuid=123456,
                    login='login',
                    password='password',
                    authId='auth_id')
        self.valid = api.ValidJSON.parse_obj(DELETE_USER)

    def tearDown(self):
        del self.valid
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True, dropJoinTables=True, cascade=True)

    @classmethod
    def tearDownClass(cls):
        pass

    def test_delete_user_response_type(self):
        self.assertIsInstance(controller.delete_user(self.valid),
                              dict)

    def test_delete_user_check_code_200(self):
        result = controller.delete_user(self.valid)
        self.assertEqual(result['errors']['code'], 200)

    def test_delete_user_check_code_401(self):
        self.dbquery = models.User.select(models.User.q.uuid == 123456)
        self.dbquery[0].authId = 'wrong_auth_id'
        result = controller.delete_user(self.valid)
        self.assertEqual(result['errors']['code'], 401)

    def test_delete_user_check_code_404(self):
        self.dbquery = models.User.select(models.User.q.uuid == 123456)
        self.dbquery[0].password = 'wrong_password'
        result = controller.delete_user(self.valid)
        self.assertEqual(result['errors']['code'], 404)


@unittest.skip('FIXME')
class TestDeleteMessage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        models.Message()

    def setUp(self):
        self.valid = api.ValidJSON.parse_obj(DELETE_MESSAGE)

    def tearDown(self):
        del self.valid

    @classmethod
    def tearDownClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True, dropJoinTables=True, cascade=True)

    def test_delete_message_response_type(self):
        self.assertIsInstance(controller.delete_message(self.valid),
                              dict)

    def test_delete_message_check_code_200(self):
        result = controller.delete_message(self.valid)
        self.assertEqual(result['errors']['code'], 200)

    def test_delete_message_check_code_404(self):
        result = controller.delete_message(self.valid)
        self.assertEqual(result['errors']['code'], 404)


class TestEditedMessage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        new_user = models.User(uuid=123456,
                               login='login',
                               password='password',
                               authId='auth_id')
        new_flow = models.Flow(flowId=123)
        models.Message(text='Hello',
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
            class_.dropTable(ifExists=True, dropJoinTables=True, cascade=True)

    def test_edited_message_response_type(self):
        self.assertIsInstance(controller.edited_message(self.valid),
                              dict)

    def test_edited_message_check_code_200(self):
        result = controller.edited_message(self.valid)
        self.assertEqual(result['errors']['code'], 200)

    def test_edited_message_check_code_401(self):
        self.valid.data.user.uuid = 654321
        result = controller.edited_message(self.valid)
        self.assertEqual(result['errors']['code'], 401)

    def test_edited_message_check_code_404(self):
        self.valid.data.message.id = 3
        print('SELF.VALID:', self.valid)
        result = controller.edited_message(self.valid)
        self.assertEqual(result['errors']['code'], 404)


class TestAllMessages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)
        new_user = models.User(uuid=123456,
                               login='login',
                               password='password',
                               authId='auth_id')
        new_user2 = models.User(uuid=654321,
                                login='login2',
                                password='password2',
                                authId='auth_id2')
        new_flow = models.Flow(flowId=123)
        new_flow2 = models.Flow(flowId=321)
        models.Message(text='Hello',
                       time=1,
                       user=new_user,
                       flow=new_flow)
        models.Message(text='Privet',
                       time=2,
                       user=new_user,
                       flow=new_flow)
        models.Message(text='Hello2',
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
            class_.dropTable(ifExists=True, dropJoinTables=True, cascade=True)

    def test_all_message_response_type(self):
        self.assertIsInstance(controller.all_messages(self.valid),
                              dict)

    def test_all_message_check_code_200(self):
        result = controller.all_messages(self.valid)
        self.assertEqual(result['errors']['code'], 200)

    def test_all_message_check_code_401(self):
        self.valid.data.user.auth_id = 'wrong_auth_id'
        result = controller.all_messages(self.valid)
        self.assertEqual(result['errors']['code'], 401)

    @unittest.skip
    def test_all_message_check_code_404(self):
        result = controller.all_messages(self.valid)
        self.assertEqual(result['errors']['code'], 404)

    def test_all_message_check_message(self):
        result = controller.all_messages(self.valid)
        self.assertEqual(result['data']['message'][3]['time'], 3)


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
            class_.dropTable(ifExists=True, dropJoinTables=True, cascade=True)

    def test_ping_pong_response_type(self):
        self.assertIsInstance(controller.ping_pong(self.valid),
                              dict)

    def test_ping_pong_chech_code_200(self):
        result = controller.ping_pong(self.valid)
        self.assertEqual(result['errors']['code'], 200)


@unittest.skip('FIXME')
class TestErrors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)

    def setUp(self):
        self.valid = api.ValidJSON.parse_obj(ERRORS)

    def tearDown(self):
        del self.valid

    @classmethod
    def tearDownClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True, dropJoinTables=True, cascade=True)

    def test_errors_response_type(self):
        self.assertIsInstance(controller.errors(self.valid),
                              dict)


if __name__ == "__main__":
    unittest.main()
