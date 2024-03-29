"""
Copyright (c) 2022 - present MoreliaTalk team and other.
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

import unittest
from unittest.mock import patch

from loguru import logger
from starlette.testclient import TestClient, WebSocketTestSession
from starlette.websockets import WebSocketDisconnect

from server import MoreliaServer


@patch("server.DBHandler")
class TestWebsocket(unittest.TestCase):
    ws_client: TestClient

    class DisconnectErr(Exception):
        pass

    @classmethod
    def setUpClass(cls):
        logger.remove()
        cls.ws_client = TestClient(MoreliaServer().get_starlette_app())

    def test_normal_connect(self, _):
        with self.ws_client.websocket_connect("/ws") as connection:
            self.assertIsInstance(connection, WebSocketTestSession)

    def test_not_websocket_endpoint_connect(self, _):
        with self.assertRaises(WebSocketDisconnect):
            with self.ws_client.websocket_connect("/no-ws"):
                pass

    def test_normal_disconnect(self, _):
        with self.ws_client.websocket_connect("/ws") as connection:
            connection.close()

    def test_not_normal_disconnect(self, _):
        with self.assertRaises(self.DisconnectErr):
            with self.ws_client.websocket_connect("/ws") as connection:
                def callback():
                    raise self.DisconnectErr

                connection.exit_stack.callback(callback)
                connection.close(1006)

    def test_send_normal_message(self, _):
        with self.ws_client.websocket_connect("/ws") as connection:
            connection.send_json({"type": "ping-pong",
                                  "data": {"user": [{}]},
                                  "jsonapi": {"version": "1.0",
                                              "revision": "17"},
                                  "meta": None})

            self.assertIsNotNone(connection.receive_json())

    def test_send_incorrect_message(self, _):
        with self.assertRaises(WebSocketDisconnect):
            with self.ws_client.websocket_connect("/ws") as connection:
                connection.send_text("hello error!")
                connection.receive_bytes()


if __name__ == "__main__":
    unittest.main()