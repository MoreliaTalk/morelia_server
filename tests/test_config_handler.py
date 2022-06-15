"""
Copyright (c) 2022 - present MoreliaTalk team and other.
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

import io
from pathlib import PurePath, Path
from unittest import TestCase
from unittest.mock import patch, Mock

import tomli_w

from mod.config.handler import ConfigHandler
from mod.config.models import ConfigModel


class TestConfigHandler(TestCase):
    @patch("mod.config.handler.Path.is_file", return_value=True)
    def test_get_fullpath_and_check_exist(self, _):
        self.assertEqual(ConfigHandler._get_fullpath(PurePath("config.toml")),
                         Path(PurePath(__file__).parent.parent, "config.toml"))

    @patch("pathlib.Path")
    @patch("mod.config.handler.ConfigHandler._get_fullpath")
    def test_read(self, mock_path, mock_get_path):
        mock_path = mock_path()

        fake_file = io.StringIO()
        mock_path.open.return_value = fake_file

        fake_toml = ConfigModel().dict()
        fake_file.write(tomli_w.dumps(fake_toml))
        mock_get_path.return_value = mock_path

        value_read = ConfigHandler("config.toml").read()

        self.assertEqual(value_read, fake_toml)

    @patch("pathlib.Path")
    @patch("mod.config.handler.ConfigHandler._get_fullpath")
    def test_str(self, mock_path, mock_get_path: Mock):
        mock_path = mock_path()

        fake_file = io.StringIO()
        mock_path.open.return_value = fake_file

        fake_toml = ConfigModel().dict()
        fake_file.write(tomli_w.dumps(fake_toml))
        mock_get_path.return_value = mock_path
        mock_get_path().__str__.return_value = "config.toml"

        self.assertRegex(ConfigHandler("config.toml").__str__(), "config.toml")
