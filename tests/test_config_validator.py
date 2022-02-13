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
from mod.config.validator import DatabaseSection
from mod.config.validator import HashSection
from mod.config.validator import LoggingSection
from mod.config.validator import TemplatesSection
from mod.config.validator import ServerLimitSection
from mod.config.validator import SuperuserSection
from mod.config.validator import AdminSection
from pydantic.error_wrappers import ValidationError


class TestConfigValidator(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_valid_database_section(self) -> None:
        test = DatabaseSection(uri=123156)
        self.assertEqual(test.dict()["uri"], "123156")

    def test_valid_hash_section(self) -> None:
        test = HashSection(password="1",
                           auth_id=12345)
        self.assertEqual(test.dict()["password"], 1)
        self.assertEqual(test.dict()["auth_id"], 12345)

    def test_valid_logging_section(self) -> None:
        test = LoggingSection(level="10",
                              expiration_date=3,
                              debug_expiration_date=0,
                              uvicorn_logging_disable=1,
                              debug="test_string",
                              error=0,
                              info="")
        self.assertEqual(test.dict()["level"], 10)
        self.assertEqual(test.dict()["expiration_date"], 3)
        self.assertEqual(test.dict()["debug_expiration_date"], 0)
        self.assertEqual(test.dict()["uvicorn_logging_disable"], True)
        self.assertEqual(test.dict()["debug"], "test_string")
        self.assertEqual(test.dict()["error"], "0")
        self.assertEqual(test.dict()["info"], "")

    def test_not_valid_logging_section(self) -> None:
        self.assertRaises(ValidationError,
                          LoggingSection,
                          level="10",
                          expiration_date=3,
                          debug_expiration_date="",
                          uvicorn_logging_disable=1,
                          debug="test_string",
                          error=0,
                          info="")

    def test_valid_templates_section(self) -> None:
        test = TemplatesSection(folder=123156)
        self.assertEqual(test.dict()["folder"], "123156")

    def test_valid_server_limit_section(self) -> None:
        test = ServerLimitSection(message="1",
                                  users=12345)
        self.assertEqual(test.dict()["message"], 1)
        self.assertEqual(test.dict()["users"], 12345)

    def test_valid_superuser_section(self) -> None:
        test = SuperuserSection(uuid=10,
                                username=33333,
                                login=0,
                                password="test_string",
                                salt="salt",
                                key=0,
                                hash_password=5555)
        self.assertEqual(test.dict()["uuid"], "10")
        self.assertEqual(test.dict()["username"], "33333")
        self.assertEqual(test.dict()["login"], "0")
        self.assertEqual(test.dict()["password"], "test_string")
        self.assertEqual(test.dict()["salt"], "salt")
        self.assertEqual(test.dict()["key"], "0")
        self.assertEqual(test.dict()["hash_password"], "5555")

    def test_valid_admin_section(self) -> None:
        test = AdminSection(secret_key=123156)
        self.assertEqual(test.dict()["secret_key"], "123156")
