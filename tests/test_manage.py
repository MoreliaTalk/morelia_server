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

import unittest
from unittest import mock

import tomli_w
from typer.testing import CliRunner

from manage import cli
from mod.config.models import ConfigModel
from mod.db.dbhandler import DatabaseAccessError


@mock.patch("uvicorn.run")
class TestDevServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cli_runner = CliRunner()


    def test_run_with_default_params(self, uvicorn_run_mock: mock.Mock) -> None:
        self.cli_runner.invoke(cli, ["devserver"])

        self.assertEqual(uvicorn_run_mock.call_count, 1)
        self.assertEqual(uvicorn_run_mock.call_args,
                         mock.call(app="server:app",
                                   host="127.0.0.1",
                                   port=8080,
                                   log_level="critical",
                                   debug=True,
                                   reload=True))

    def test_run_with_custom_params(self, uvicorn_run_mock: mock.Mock) -> None:
        self.cli_runner.invoke(cli, ("devserver",
                                     "--host", "0.0.0.0",
                                     "--port", 8081,
                                     "--on-uvicorn-logger"))

        self.assertEqual(uvicorn_run_mock.call_count, 1)
        self.assertEqual(uvicorn_run_mock.call_args,
                         mock.call(app="server:app",
                                   host="0.0.0.0",
                                   port=8081,
                                   log_level="debug",
                                   debug=True,
                                   reload=True))


class TestRestoreConfig(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cli_runner = CliRunner()

    @mock.patch("pathlib.Path.open", new_callable=mock.mock_open)
    def test_restore_config(self, file_open_mock: mock.Mock) -> None:
        runner_result = self.cli_runner.invoke(cli, "restore-config", input="y")

        default_dict = ConfigModel().dict()
        default_toml = tomli_w.dumps(default_dict)

        self.assertEqual(runner_result.output, "This action is not reversible. "
                                               "The config will be overwritten with default data. "
                                               "Continue? [y/N]: y\n"
                                               "Successful restore config\n")

        self.assertIn(mock.call().write(default_toml),
                      file_open_mock.mock_calls)

    def test_with_answer_no(self):
        runner_result = self.cli_runner.invoke(cli, "restore-config", input="N")

        self.assertEqual(runner_result.output, "This action is not reversible. "
                                               "The config will be overwritten with default data. "
                                               "Continue? [y/N]: N\n"
                                               "Canceled!\n")

@mock.patch("manage.DBHandler")
class TestCreateTables(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cli_runner = CliRunner()

    def test_successful_create_table(self, dbhandler_mock: mock.Mock):
        runner_result = self.cli_runner.invoke(cli, "create-tables")

        self.assertEqual(dbhandler_mock().create_table.call_count, 1)
        self.assertEqual(runner_result.output, "Tables in db successful created.\n")

    def test_database_not_available(self, dbhandler_mock: mock.Mock):
        dbhandler_mock().create_table.side_effect = DatabaseAccessError()

        runner_result = self.cli_runner.invoke(cli, "create-tables")

        self.assertEqual(runner_result.output, f"The database is unavailable, "
                                               f"table not created. {DatabaseAccessError()}\n")

@mock.patch("manage.DBHandler")
class TestDeleteTables(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cli_runner = CliRunner()

    def test_successful_delete_tables(self, dbhandler_mock: mock.Mock):
        runner_result = self.cli_runner.invoke(cli, "delete-tables")

        self.assertEqual(dbhandler_mock().delete_table.call_count, 1)
        self.assertEqual(runner_result.output, "Tables in db successful deleted.\n")

    def test_database_not_available(self, dbhandler_mock: mock.Mock):
        dbhandler_mock().delete_table.side_effect = DatabaseAccessError()

        runner_result = self.cli_runner.invoke(cli, "delete-tables")

        self.assertEqual(runner_result.output, f"The database is unavailable, "
                                               f"table not deleted. {DatabaseAccessError()}\n")

@mock.patch("manage.Hash")
@mock.patch("manage.uuid4")
@mock.patch("manage.DBHandler")
class TestCreateUser(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cli_runner = CliRunner()


    @mock.patch("manage.faker_data_generator")
    def test_run_with_default_params(self,
                                     faker_generator_mock: mock.Mock,
                                     dbhandler_mock: mock.Mock,
                                     uuid4_mock: mock.Mock,
                                     hash_class_mock: mock.Mock,):
        uuid4_mock().int = 123456

        faker_generator_mock.password.return_value = "password"
        faker_generator_mock.profile.return_value = {
            "username": "some_username"
        }

        hash_class_mock().password_hash.return_value = "password_hash"

        self.cli_runner.invoke(cli, ["create-user", "login"])

        self.assertEqual(dbhandler_mock().add_user.call_count, 1)
        self.assertEqual(dbhandler_mock().add_user.call_args,
                         mock.call(uuid=str(123456),
                                   login="login",
                                   password="password",
                                   hash_password="password_hash",
                                   username="some_username",
                                   salt=b"salt",
                                   key=b"key"))

    def test_run_with_custom_params(self,
                                    dbhandler_mock: mock.Mock,
                                    uuid4_mock: mock.Mock,
                                    hash_class_mock: mock.Mock):
        uuid4_mock().int = 123456

        hash_class_mock().password_hash.return_value = "password_hash"

        self.cli_runner.invoke(cli, ["create-user",
                                           "--username=some_user_123",
                                           "--password=Hello123",
                                           "login"
                                           ])

        self.assertEqual(dbhandler_mock().add_user.call_count, 1)
        self.assertEqual(dbhandler_mock().add_user.call_args,
                         mock.call(uuid=str(123456),
                                   login="login",
                                   password="Hello123",
                                   hash_password="password_hash",
                                   username="some_user_123",
                                   salt=b"salt",
                                   key=b"key"))

if __name__ == "__main__":
    unittest.main()
