import unittest
import sys
import os
import json

sys.path.append(os.path.dirname(os.getcwd()))
from mod import controller
from mod import api


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


class TestAllMessages(unittest.TestCase):
    def setUp(self):
        all_messages_dict = {
            'type': 'all_messages',
            'data': {
                'time': 1594492370,
                'user': {
                    'uuid': 111111111,
                    'auth_id': 'dks7sd9f6g4fg67vb78g65'
                    },
                'meta': None
                },
            'jsonapi': {
                'version': '1.0'
                },
            'meta': None
            }
        all_messages_json = json.dumps(all_messages_dict)
        self.test_dict = api.ValidJSON.parse_raw(all_messages_json)

    def test_all_messages_return_type_dict(self):
        self.assertIsInstance(controller.all_messages(self.test_dict),
                              dict)

    def test_all_messages_is_in_dict(self):
        self.assertEqual('all_messages',
                         controller.all_messages(self.test_dict)['type'])

    def tearDown(self):
        self.test_dict = {}


class TestPingPong(unittest.TestCase):
    def setUp(self):
        ping_pong_dict = {
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
        ping_pong_json = json.dumps(ping_pong_dict)
        self.test_dict = api.ValidJSON.parse_raw(ping_pong_json)

    def test_ping_pong_return_type_dict(self):
        self.assertIsInstance(controller.ping_pong(self.test_dict), dict)

    def test_ping_pong_is_in_dict(self):
        self.assertEqual('ping-pong', controller.ping_pong(self.test_dict)['type'])

    def tearDown(self):
        self.test_dict = {}


if __name__ == "__main__":
    unittest.main()
