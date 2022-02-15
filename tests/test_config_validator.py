"""
    Copyright (c) 2022 - present NekrodNIK, Stepan Skriabin, rus-ai and other.
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
from mod.config.validator import ConfigModel
from pydantic.error_wrappers import ValidationError


class TestConfigValidator(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_valid_database_section(self) -> None:
        test = ConfigModel(uri=123156,
                           password="1",
                           auth_id=12345,
                           level="10",
                           expiration_date=3,
                           debug_expiration_date=0,
                           uvicorn_logging_disable=1,
                           debug="test_string",
                           error=0,
                           info="",
                           folder=123156,
                           message="1",
                           users=12345,
                           secret_key=123156)
        self.assertEqual(test.dict()["uri"], "123156")
        self.assertEqual(test.dict()["password"], 1)
        self.assertEqual(test.dict()["auth_id"], 12345)
        self.assertEqual(test.dict()["level"], 10)
        self.assertEqual(test.dict()["expiration_date"], 3)
        self.assertEqual(test.dict()["debug_expiration_date"], 0)
        self.assertEqual(test.dict()["uvicorn_logging_disable"], True)
        self.assertEqual(test.dict()["debug"], "test_string")
        self.assertEqual(test.dict()["error"], "0")
        self.assertEqual(test.dict()["info"], "")
        self.assertEqual(test.dict()["folder"], "123156")
        self.assertEqual(test.dict()["message"], 1)
        self.assertEqual(test.dict()["users"], 12345)
        self.assertEqual(test.dict()["secret_key"], "123156")

    def test_not_valid_logging_section(self) -> None:
        self.assertRaises(ValidationError,
                          ConfigModel,
                          uri=123156,
                          password="1",
                          auth_id=12345,
                          level="10",
                          expiration_date=3,
                          debug_expiration_date="",
                          uvicorn_logging_disable=1,
                          debug="test_string",
                          error=0,
                          info="",
                          folder=123156,
                          message="1",
                          users=12345,
                          secret_key=123156)
