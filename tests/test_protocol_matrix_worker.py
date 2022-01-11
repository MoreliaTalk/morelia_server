"""
    Copyright (c) 2020 - present NekrodNIK, Stepan Skriabin, rus-ai and other.
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
from uuid import uuid4

from loguru import logger

from mod.protocol.matrix.worker import MatrixProtocol


# Add path to directory with code being checked
# to variable 'PATH' to import modules from directory
# above the directory with the tests.
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
FIXTURES_PATH = os.path.join(BASE_PATH, "fixtures")

GET_UPDATE = os.path.join(FIXTURES_PATH, "get_update.json")
SEND_MESSAGE = os.path.join(FIXTURES_PATH, "send_message.json")
ALL_MESSAGES = os.path.join(FIXTURES_PATH, "all_message.json")
ADD_FLOW = os.path.join(FIXTURES_PATH, "add_flow.json")
ALL_FLOW = os.path.join(FIXTURES_PATH, "all_flow.json")
USER_INFO = os.path.join(FIXTURES_PATH, "user_info.json")
REGISTER_USER = os.path.join(FIXTURES_PATH, "register_user.json")
AUTH = os.path.join(FIXTURES_PATH, "auth.json")
DELETE_USER = os.path.join(FIXTURES_PATH, "delete_user.json")
DELETE_MESSAGE = os.path.join(FIXTURES_PATH, "delete_message.json")
EDITED_MESSAGE = os.path.join(FIXTURES_PATH, "edited_message.json")
PING_PONG = os.path.join(FIXTURES_PATH, "ping_pong.json")
ERRORS = os.path.join(FIXTURES_PATH, "errors.json")
NON_VALID_ERRORS = os.path.join(FIXTURES_PATH, "non_valid_errors.json")
ERRORS_ONLY_TYPE = os.path.join(FIXTURES_PATH, "errors_only_type.json")


class TestGetResponse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()

    def setUp(self):
        self.test_words = "Method not worked"

    def tearDown(self):
        del self.test_words

    def test_check_get_response(self):
        result = MatrixProtocol.get_response()
        self.assertIsInstance(result, str)
        self.assertEqual(result,
                         self.test_words)


if __name__ == "__main__":
    unittest.main()
