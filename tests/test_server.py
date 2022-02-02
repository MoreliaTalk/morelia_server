import json
import logging

from starlette.testclient import TestClient, WebSocketTestSession

from config import LOGGING
from server import app
import unittest

if LOGGING.getboolean("UVICORN_LOGGING_DISABLE"):
    logging.disable()


class TestWebsocket(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ws_client = TestClient(app)

    def test_normal_connect(self):
        with self.ws_client.websocket_connect("/ws") as connection:
            self.assertIsInstance(connection, WebSocketTestSession)

    def test_normal_disconnect(self):
        with self.ws_client.websocket_connect("/ws") as connection:
            connection.close()

    def test_not_normal_disconnect(self):
        with self.ws_client.websocket_connect("/ws") as connection:
            connection.close(1006)

    def test_send_normal_message(self):
        with self.ws_client.websocket_connect("/ws") as connection:
            connection.send_json(json.dumps({}))

    def test_send_incorrect_message(self):
        with self.ws_client.websocket_connect("/ws") as connection:
            connection.send_text("hello error!")


class TestMainPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_client = TestClient(app)

    def test_main_page(self):
        response = self.test_client.get("/")
        self.assertEqual(response.text, "<h1>MoreliaTalkServer</h1>")
