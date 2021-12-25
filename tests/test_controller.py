"""
    Copyright (c) 2021 - present NekrodNIK, Stepan Skriabin, rus-ai and other.
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
import json
import os
import unittest

from loguru import logger

from mod.db.dbhandler import DBHandler
from mod.protocol.mtp import api
from mod.controller import MainHandler

BASE_PATH = os.path.abspath(os.path.dirname(__file__))
FIXTURES_PATH = os.path.join(BASE_PATH, "fixtures")

GET_UPDATE = os.path.join(FIXTURES_PATH, "get_update.json")


class TestController(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()
        cls.db = DBHandler(uri='sqlite:/:memory:')

    def setUp(self) -> None:
        self.db.create()
        self.db.add_user(uuid="123456",
                         login="login",
                         password="password",
                         auth_id="auth_id")
        self.db.add_user(uuid="987654",
                         login="login2",
                         password="password2",
                         auth_id="auth_id2")
        self.db.add_flow(uuid="07d949",
                         users=["123456",
                                "987654"],
                         time_created=111,
                         flow_type="chat",
                         title="title1",
                         info="info1",
                         owner="123456")
        self.db.add_message(flow_uuid="07d949",
                            user_uuid="123456",
                            message_uuid="111",
                            text="Hello1",
                            time=111)
        self.db.add_message(flow_uuid="07d949",
                            user_uuid="987654",
                            message_uuid="112",
                            text="Hello2",
                            time=222)
        self.test = api.Request.parse_file(GET_UPDATE)

    def tearDown(self) -> None:
        self.db.delete()

    @classmethod
    def tearDownClass(cls) -> None:
        del cls.db

    def test_main_handler(self):
        run_handler = MainHandler(self.test,
                                  self.db,
                                  protocol='mtp')
        result = json.loads(run_handler.get_response())
        self.assertIsInstance(result, dict)
        self.assertEqual(result['jsonapi']['version'], "1.0")

    def test_mtp_handler(self):
        run_handler = MainHandler(self.test,
                                  self.db,
                                  protocol='mtp')
        result = json.loads(run_handler.mtp_handler())
        self.assertEqual(result['errors']['status'], 'OK')
        self.assertEqual(result['type'], 'get_update')

    @unittest.skip('Matrix protocol is not implemented')
    def test_matrix_handler(self):
        pass
