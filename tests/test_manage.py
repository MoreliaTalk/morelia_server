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

from typer.testing import CliRunner
from manage import cli


class TestDevServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cli_runner = CliRunner()

    @mock.patch("uvicorn.run")
    def test_run_with_default_params(self, uvicorn_run_mock: mock.Mock):
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
    def test_run_with_custom_params(self, uvicorn_run: mock.Mock):
        self.cli_runner.invoke(cli, ("devserver",
                                     "--host", "0.0.0.0",
                                     "--port", 8081,
                                     "--on-uvicorn-logger"))

        self.assertEqual(uvicorn_run.call_count, 1)
        self.assertEqual(uvicorn_run.call_args,
                         mock.call(app="server:app",
                                   host="0.0.0.0",
                                   port=8081,
                                   log_level="debug",
                                   debug=True,
                                   reload=True))


if __name__ == "__main__":
    unittest.main()
