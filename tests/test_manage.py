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
from typer.testing import CliRunner
from manage import cli
from unittest.mock import patch, Mock


class TestManage(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cli_runner = CliRunner()

    @patch("uvicorn.run")
    def test_devserver(self, uvicorn_run: Mock):
        self.cli_runner.invoke(cli, ["devserver"])
        self.assertEqual(uvicorn_run.call_count, 1)



if __name__ == "__main__":
    unittest.main()
