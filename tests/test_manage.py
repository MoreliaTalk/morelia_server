"""
Copyright (c) 2020 - present MoreliaTalk team and other.
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

from pathlib import PurePath
import unittest
from unittest.mock import patch
from uuid import uuid4

from click.testing import CliRunner
from loguru import logger

from manage import delete
from manage import client
from manage import create
from manage import run

from mod.db.dbhandler import DBHandler
from mod.lib import Hash


class TestManage(unittest.TestCase):
    uri: str
    db: DBHandler
    path: PurePath

    @classmethod
    def setUpClass(cls) -> None:
        logger.remove()
        cls.uri = "sqlite:/:memory:?cache=shared"
        cls.db = DBHandler(uri=cls.uri)

    def setUp(self) -> None:
        self.username = "UserHello"
        self.login = "login123"
        self.password = "password123"
        self.user_uuid = str(uuid4().int)
        self.runner = CliRunner()
        self.hash = Hash(self.password,
                         self.user_uuid)

    def tearDown(self) -> None:
        self.db.delete_table()
        del self.runner

    @classmethod
    def tearDownClass(cls) -> None:
        cls.db.delete_table()
        del cls.db

    def test_create_user(self):
        self.db.create_table()
        result = self.runner.invoke(create,
                                    [f"--uri={self.uri}",
                                     "user",
                                     f"--username={self.username}",
                                     f"--login={self.login}",
                                     f"--password={self.password}"])
        self.assertRegex(result.output,
                         f"User with name={self.username}, login=")

    def test_create_flow(self):
        self.db.create_table()
        self.db.add_user(uuid=self.user_uuid,
                         login=self.login,
                         password=self.password,
                         hash_password=self.hash.password_hash(),
                         username=self.username,
                         salt=b"salt",
                         key=b"key")
        result = self.runner.invoke(create,
                                    [f"--uri={self.uri}",
                                     "flow",
                                     f"--login={self.login}"])
        self.assertRegex(result.stdout, "Flow created.")

    def test_create_admin(self):
        result = self.runner.invoke(create,
                                    [f"--uri={self.uri}",
                                     "admin",
                                     f"--username={self.username}",
                                     f"--password={self.password}"])
        self.assertRegex(result.output, "Admin created.")

    def test_create_db(self):
        result = self.runner.invoke(create,
                                    [f"--uri={self.uri}",
                                     "db"])
        self.assertRegex(result.stdout,
                         "Database is created.")

    def test_delete_db(self):
        self.db.create_table()
        result = self.runner.invoke(delete,
                                    [f"--uri={self.uri}",
                                     "db"])
        self.assertRegex(result.output,
                         "All table is deleted.")

    @patch('pathlib.Path.is_file', return_value=True)
    @patch('os.remove', return_value=None)
    def test_clean_init(self, _, __):
        result = self.runner.invoke(run,
                                    ["clean",
                                     "--yes"])
        self.assertEqual(result.stdout,
                         "".join(("Config file => deleted.\n",
                                  "Database file => deleted.\n")))

    @patch('pathlib.Path.is_file', return_value=False)
    @patch('os.remove', return_value=None)
    def test_error_in_clean_init(self, _, __):
        result = self.runner.invoke(run,
                                    ["clean",
                                     "--yes"])
        self.assertEqual(result.stdout,
                         "".join(("Config file is not found => NOT deleted.\n",
                                  "Database file is not found => NOT deleted.\n")))

    @patch('manage.create_table', return_value=None)
    @patch('manage.create_administrator', return_value=None)
    def test_init(self, _, __):
        result = self.runner.invoke(run,
                                    ["init",
                                     f"--username={self.username}",
                                     f"--password={self.password}"])
        self.assertRegex(result.stdout, "Database => Ok")
        self.assertRegex(result.stdout, "admin => Ok")

    @patch('uvicorn.run', return_value=None)
    def test_devserver(self, _):
        result = self.runner.invoke(run,
                                    ["devserver"])
        self.assertRegex(result.stdout, "Develop server started at address=")

    @patch('uvicorn.run', return_value=None)
    def test_server(self, _):
        result = self.runner.invoke(run,
                                    ["server"])
        self.assertRegex(result.stdout, "Server started at address=")

    def test_client_without_connection_to_server(self):
        result = self.runner.invoke(client,
                                    ["send"])
        self.assertRegex(result.stdout, "Unable to connect to the server")


if __name__ == "__main__":
    unittest.main()
