import inspect
import json
import os
import sys
import unittest

import sqlobject as orm

sys.path.append(os.path.dirname(os.getcwd()))
from mod import api
from mod import config
from mod import controller
from mod import models

connection = orm.connectionForURI('sqlite:/:memory:')
orm.sqlhub.processConnection = connection

classes = [cls_name for cls_name, cls_obj
           in inspect.getmembers(sys.modules['mod.models'])
           if inspect.isclass(cls_obj)]

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
      "password": "ds45ds45fd45fd",
      "login": "User"
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
      "password": "ds45ds45fd45fd",
      "login": "User"
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

EDITED_MESSAGE = {
  "type": "edited_message",
  "data": {
      "message": {
        "id": 858585,
        "text": "Hello!",
        "time": 1594492370
        },
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
        "uuid": 111111111,
        "username": "User"
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
      "uuid": 111111111,
      "auth_id": "dks7sd9f6g4fg67vb78g65",
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
    "time": 1594492370,
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

ADD_FLOW = {}
# end sample


@unittest.skip
class TestServeRequest(unittest.TestCase):
    def setUp(self):
        self.serve_request_dict = {
            'type': 'ping-pong',
            'data': {
                'user': {
                    'uuid': 5345634567354,
                    'auth_id': 'lkds89ds89fd98fd'
                    },
                'meta': None
                },
            'jsonapi': {
                'version': '1.0'
                },
            'meta': None
            }
        self.serve_request_json = json.dumps(self.serve_request_dict)

    def test_serve_request_type_dict(self):
        self.assertIsInstance(controller.serve_request(self.serve_request_json),
                              dict)

    def testserve_request_validation_error(self):
        self.assertIsInstance(controller.serve_request(self.serve_request_dict),
                              dict)

    def testserve_request_validation_error_type(self):
        self.assertIn('error',
                      controller.serve_request(self.serve_request_dict)['type'])

    def tearDown(self):
        self.serve_request_dict = {}
        self.serve_request_json = {}


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


class TestGetUpdate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)

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
        self.assertIsInstance(controller.register_user(self.valid),
                              dict)


class TestSendMessage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)

    def setUp(self):
        self.valid = api.ValidJSON.parse_obj(SEND_MESSAGE)

    def tearDown(self):
        del self.valid

    @classmethod
    def tearDownClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True, dropJoinTables=True, cascade=True)

    def test_send_message_response_type(self):
        self.assertIsInstance(controller.register_user(self.valid),
                              dict)


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
        self.assertIsInstance(controller.register_user(self.valid),
                              dict)


class TestAllFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)

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


class TestUserInfo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)

    def setUp(self):
        self.valid = api.ValidJSON.parse_obj(USER_INFO)

    def tearDown(self):
        del self.valid

    @classmethod
    def tearDownClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True, dropJoinTables=True, cascade=True)

    def test_user_info_response_type(self):
        self.assertIsInstance(controller.register_user(self.valid),
                              dict)


class TestAuthentification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)

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
        self.assertIsInstance(controller.register_user(self.valid),
                              dict)


class TestDeleteUser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)

    def setUp(self):
        self.valid = api.ValidJSON.parse_obj(DELETE_USER)

    def tearDown(self):
        del self.valid

    @classmethod
    def tearDownClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True, dropJoinTables=True, cascade=True)

    def test_delete_user_response_type(self):
        self.assertIsInstance(controller.register_user(self.valid),
                              dict)


class TestDeleteMessage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)

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
        self.assertIsInstance(controller.register_user(self.valid),
                              dict)


class TestEditedMessage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)

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
        self.assertIsInstance(controller.register_user(self.valid),
                              dict)


class TestAllMessages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for item in classes:
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True)

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
        self.assertIsInstance(controller.register_user(self.valid),
                              dict)


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
        self.assertIsInstance(controller.register_user(self.valid),
                              dict)


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
        self.assertIsInstance(controller.register_user(self.valid),
                              dict)


if __name__ == "__main__":
    unittest.main()
