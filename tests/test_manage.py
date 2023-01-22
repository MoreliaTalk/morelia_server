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


class TestDevServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cli_runner = CliRunner()

    @mock.patch("uvicorn.run")
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

    @mock.patch("uvicorn.run")
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


if __name__ == "__main__":
    unittest.main()
