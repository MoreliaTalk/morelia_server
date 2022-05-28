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

from pathlib import Path, PurePath
from typing import Any
import unittest

from click.testing import CliRunner
from loguru import logger
from manage import db_cli

from mod.config.config import ConfigHandler
from mod.db.dbhandler import DBHandler


class TestCreateUserAndFlowAndAdmin(unittest.TestCase):
    db_uri: str
    config: ConfigHandler
    config_option: Any
    db: DBHandler
    path: PurePath

    @classmethod
    def setUpClass(cls) -> None:
        logger.remove()
        cls.config = ConfigHandler()
        cls.config_option = cls.config.read()
        cls.db_uri = "sqlite:/:memory:?cache=shared"
        cls.db = DBHandler(uri=cls.db_uri)
        cls.db.create_table()

    def setUp(self) -> None:
        self.username = "UserHello"
        self.login = "login123"
        self.password = "password123"
        self.runner = CliRunner()

    def tearDown(self) -> None:
        del self.runner

    @classmethod
    def tearDownClass(cls) -> None:
        cls.db.delete_table()
        del cls.db

    def test_create_user(self):
        result = self.runner.invoke(db_cli, [f"--uri={self.db_uri}",
                                             "user-create",
                                             f"--username={self.username}",
                                             f"--login={self.login}",
                                             f"--password={self.password}"])
        self.assertEqual(result.exit_code, 0)
        self.assertRegex(result.output,
                         f"{self.username} created, login: {self.login}, "
                         f"password: {self.password}")

    def test_wrong_create_user(self):
        self.db.delete_table()
        result = self.runner.invoke(db_cli, [f"--uri={self.db_uri}",
                                             "user-create",
                                             f"--username={self.username}",
                                             f"--login={self.login}",
                                             f"--password={self.password}"])
        self.assertRegex(result.stdout,
                         "Failed to create a user. Error text:")

    def test_create_flow(self):
        self.runner.invoke(db_cli, [f"--uri={self.db_uri}",
                                    "user-create",
                                    f"--username={self.username}",
                                    f"--login={self.login}",
                                    f"--password={self.password}"])
        result = self.runner.invoke(db_cli, [f"--uri={self.db_uri}",
                                             "flow-create",
                                             f"--login={self.login}"])
        self.assertEqual(result.stdout, "Flow created\n")

    def test_wrong_create_flow(self):
        result = self.runner.invoke(db_cli, [f"--uri={self.db_uri}",
                                             "flow-create",
                                             f"--login={self.login}"])
        self.assertRegex(result.stdout,
                         "Failed to create a flow. Error text: ")

    def test_create_admin_user(self):
        result = self.runner.invoke(db_cli, [f"--uri={self.db_uri}",
                                             "admin-create",
                                             f"--username={self.username}",
                                             f"--password={self.password}"])
        self.assertRegex(result.stdout, "Admin created\nusername: ")

    def test_wrong_create_admin_user(self):
        self.db.delete_table()
        result = self.runner.invoke(db_cli, [f"--uri={self.db_uri}",
                                             "admin-create",
                                             f"--username={self.username}",
                                             f"--password={self.password}"])
        self.assertRegex(result.stdout,
                         "Failed to create a flow. Error text:")


class TestDBCli(unittest.TestCase):
    db_uri: str

    @classmethod
    def setUpClass(cls) -> None:
        logger.remove()
        cls.db_uri = "sqlite:/:memory:"

    def setUp(self) -> None:
        self.runner = CliRunner()

    def tearDown(self) -> None:
        del self.runner

    def test_db_create(self):
        result = self.runner.invoke(db_cli, [f"--uri={self.db_uri}",
                                             "create"])
        self.assertEqual(result.exit_code, 0)
        self.assertRegex(result.stdout, "Table is created at: ")

    def test_db_delete(self):
        self.runner.invoke(db_cli, [f"--uri={self.db_uri}",
                                    "create"])
        result = self.runner.invoke(db_cli, [f"--uri={self.db_uri}",
                                             "delete"])
        self.assertRegex(result.stdout, "Table is deleted at: ")


if __name__ == "__main__":
    unittest.main()
