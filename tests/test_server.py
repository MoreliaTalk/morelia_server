import json

from starlette.testclient import TestClient, WebSocketTestSession
from starlette.websockets import WebSocketDisconnect

import unittest

from loguru import logger
logger.disable("")

from server import app


class TestWebsocket(unittest.TestCase):
    class DisconnectErr(Exception):
        pass

    @classmethod
    def setUpClass(cls):
        cls.ws_client = TestClient(app)

    def test_normal_connect(self):
        with self.ws_client.websocket_connect("/ws") as connection:
            self.assertIsInstance(connection, WebSocketTestSession)

    def test_not_websocket_endpoint_connect(self):
        with self.assertRaises(WebSocketDisconnect):
            with self.ws_client.websocket_connect("/no-ws"):
                pass

    def test_normal_disconnect(self):
        with self.ws_client.websocket_connect("/ws") as connection:
            connection.close()

    def test_not_normal_disconnect(self):
        with self.assertRaises(self.DisconnectErr):
            with self.ws_client.websocket_connect("/ws") as connection:
                def callback():
                    raise self.DisconnectErr

                connection.exit_stack.callback(callback)
                connection.close(1006)

    def test_send_normal_message(self):
        with self.ws_client.websocket_connect("/ws") as connection:
            connection.send_json({"type": "ping-pong",
                                  "data": {"user": [{}]},
                                  "jsonapi": {"version": "1.0",
                                              "revision": "17"},
                                  "meta": None})
            self.assertIsNotNone(json.loads(connection.receive_bytes()))

    def test_send_incorrect_message(self):
        with self.assertRaises(WebSocketDisconnect):
            with self.ws_client.websocket_connect("/ws") as connection:
                connection.send_text("hello error!")
                connection.receive_bytes()


class TestMainPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_client = TestClient(app)

    def test_main_page(self):
        response = self.test_client.get("/")
        self.assertEqual(response.text, "<h1>MoreliaTalkServer</h1>")
