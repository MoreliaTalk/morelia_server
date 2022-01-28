"""
    Copyright (c) 2020 - present NekrodNIK, Stepan Skriabin, rus-ai and other.
    Look at the file AUTHORS.md(located at the root of the project) to get the full list.

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

import os
import sys
import unittest
from loguru import logger

from pydantic.error_wrappers import ValidationError

from mod.protocol.mtp import api

# Add path to directory with code being checked
# to variable 'PATH' to import modules from directory
# above the directory with tests.
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
FIXTURES_PATH = os.path.join(BASE_PATH, 'fixtures')
VALID_JSON = os.path.join(FIXTURES_PATH, 'valid.json')
WRONG_JSON = os.path.join(FIXTURES_PATH, 'wrong.json')
WRONG_REQUEST = os.path.join(FIXTURES_PATH, 'wrong_request.json')
WRONG_RESPONSE = os.path.join(FIXTURES_PATH, 'wrong_response.json')
WRONG_DATA_ERRORS = os.path.join(FIXTURES_PATH, 'wrong_data_errors.json')
WRONG_FLOW_MESSAGE = os.path.join(FIXTURES_PATH, 'wrong_flow_message.json')
sys.path.append(os.path.split(BASE_PATH)[0])


class TestApiValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()

    def setUp(self):
        self.valid = api.Request.parse_file(VALID_JSON)
        self.test = "API VALIDATION SCHEME IS WRONG"

    def tearDown(self):
        del self.valid

    def test_validation_valid_json(self):
        result = self.valid.dict()
        self.assertIsInstance(result, dict)
        self.assertEqual(result['data']['user'][0]['token_ttl'],
                         123456123456)
        self.assertEqual(result['data']['message'][0]['client_id'],
                         123456)
        self.assertEqual(result['jsonapi']['version'], '1.0')
        self.assertEqual(result['jsonapi']['revision'], '17')

    def test_validation_wrong_json(self):
        try:
            api.Request.parse_file(WRONG_JSON)
        except ValidationError as error:
            self.assertEqual(ValidationError, type(error))

    def test_api_request(self):
        try:
            api.Request.parse_file(WRONG_REQUEST)
        except Exception as err:
            result = err.errors()
            self.assertEqual(result[0].get("msg"),
                             "str type expected")
            self.assertEqual(result[1].get("msg"),
                             "field required")
            self.assertEqual(result[2].get("msg"),
                             "field required")
            self.assertEqual(result[3].get("msg"),
                             "value is not a valid integer")
            self.assertEqual(result[4].get("msg"),
                             "str type expected")
            self.assertEqual(result[5].get("msg"),
                             "value is not a valid integer")
        else:
            self.assertIsNone(self.test)

    def test_api_response(self):
        try:
            api.Response.parse_file(WRONG_RESPONSE)
        except Exception as err:
            result = err.errors()
            self.assertEqual(result[0].get("msg"),
                             "field required")
            self.assertEqual(result[1].get("msg"),
                             "value is not a valid integer")
            self.assertEqual(result[2].get("msg"),
                             "field required")
            self.assertEqual(result[3].get("msg"),
                             "field required")
            self.assertEqual(result[4].get("msg"),
                             "field required")
        else:
            self.assertIsNone(self.test)

    def test_api_jsonapi(self):
        result = self.valid.dict()
        self.assertEqual(result['jsonapi']['version'], '1.0')
        self.assertEqual(result['jsonapi']['revision'], '17')

    def test_api_wrong_data_and_errors_in_request(self):
        try:
            api.Request.parse_file(WRONG_DATA_ERRORS)
        except Exception as err:
            result = err.errors()
            self.assertEqual(result[0].get("msg"),
                             "value is not a valid dict")
            self.assertEqual(result[1].get("msg"),
                             "value is not a valid dict")
        else:
            self.assertIsNone(self.test)

    def test_api_wrong_flow_and_message_in_request(self):
        try:
            api.Request.parse_file(WRONG_FLOW_MESSAGE)
        except Exception as err:
            result = err.errors()
            self.assertEqual(result[0].get("msg"),
                             "value is not a valid list")
            self.assertEqual(result[1].get("msg"),
                             "value is not a valid list")
        else:
            self.assertIsNone(self.test)


if __name__ == "__main__":
    unittest.main()
