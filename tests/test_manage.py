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

import os
import stat
from pathlib import Path, PurePath
import time
import unittest

from click.testing import CliRunner
import manage
from mod.config.config import ConfigHandler
from mod.db.dbhandler import DBHandler


class TestCreateUserAndFlowAndAdmin(unittest.TestCase):
    def setUp(self) -> None:
        self.username = "UserHello"
        self.login = "login123"
        self.password = "password123"
        self.runner = CliRunner()
        self.path = PurePath(Path.cwd(), "db_sqlite.db")
        self.config = ConfigHandler()
        self.config_option = self.config.read()
        self.db = DBHandler(uri=self.config_option.uri)
        self.db.create_table()

    def tearDown(self) -> None:
        os.remove(self.path)
        del self.runner

    def test_create_user(self):
        result = self.runner.invoke(manage.create_user,
                                    ["--username",
                                     f"{self.username}",
                                     "--login",
                                     f"{self.login}",
                                     "--password",
                                     f"{self.password}"])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output,
                         f"{self.username} created, login: {self.login}, "
                         f"password: {self.password}\n")

    def test_wrong_create_user(self):
        self.db.delete_table()
        result = self.runner.invoke(manage.create_user,
                                    ["--username",
                                     f"{self.username}",
                                     "--login",
                                     f"{self.login}",
                                     "--password",
                                     f"{self.password}"])
        self.assertRegex(result.stdout,
                         "Failed to create a user. Error text:")
        os.chmod(path=self.path,
                 mode=stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

    def test_create_flow(self):
        self.runner.invoke(manage.create_user,
                           ["--username",
                            f"{self.username}",
                            "--login",
                            f"{self.login}",
                            "--password",
                            f"{self.password}"])
        result = self.runner.invoke(manage.create_flow,
                                    ["--login", f"{self.login}"])
        self.assertEqual(result.stdout, "Flow created\n")

    def test_wrong_create_flow(self):
        result = self.runner.invoke(manage.create_flow,
                                    ["--login", f"{self.login}"])
        self.assertRegex(result.stdout,
                         "Failed to create a flow. Error text: ")

    def test_create_admin_user(self):
        result = self.runner.invoke(manage.admin_create_user,
                                    ["--username",
                                     f"{self.username}",
                                     "--password",
                                     f"{self.password}"])
        self.assertRegex(result.stdout, "Admin created\nusername: ")

    def test_wrong_create_admin_user(self):
        self.db.delete_table()
        result = self.runner.invoke(manage.admin_create_user,
                                    ["--username",
                                     f"{self.username}",
                                     "--password",
                                     f"{self.password}"])
        self.assertRegex(result.stdout,
                         "Failed to create a flow. Error text:")


class TestDBCli(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.path = PurePath(Path.cwd(), "db_sqlite.db")

    def tearDown(self) -> None:
        os.remove(self.path)
        del self.runner, self.path

    def test_db_create(self):
        result = self.runner.invoke(manage.db_create)
        self.assertRegex(result.stdout, "Table is created at: ")

    def test_db_delete(self):
        self.runner.invoke(manage.db_create)
        result = self.runner.invoke(manage.db_delete)
        self.assertRegex(result.stdout, "Table is deleted at: ")



if __name__ == "__main__":
    unittest.main()
