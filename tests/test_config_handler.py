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
from pathlib import PurePath
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from mod.config.handler import ConfigHandler
from mod.config.handler import IniParser
from mod.config.models import ConfigModel


class TestIniParser(TestCase):
    def test_loads(self):
        parsed = IniParser.loads("[db] \n uri=ok")
        self.assertEqual(parsed["db"]["uri"], "ok")

    def test_dumps(self):
        data = {
            "db": {
                "uri": "ok"
            }
        }
        ini = IniParser.dumps(data)

        self.assertRegex(ini, "[db]")
        self.assertRegex(ini, "uri = ok")


class TestConfigHandler(TestCase):
    @patch("mod.config.handler.Path.is_file", return_value=True)
    def test_get_fullpath(self, _):
        self.assertEqual(ConfigHandler._get_fullpath(PurePath("config.toml")),
                         Path(PurePath(__file__).parent.parent, "config.toml"))

    @patch("pathlib.Path")
    @patch("mod.config.handler.ConfigHandler._get_fullpath")
    def test_read(self, mock_path, mock_get_path):
        mock_path = mock_path()

        fake_file = io.StringIO()
        mock_path.open.return_value = fake_file
        mock_get_path.return_value = mock_path

        fake_model = ConfigModel()
        fake_file.write(IniParser.dumps(fake_model.dict()))

        value_read = ConfigHandler("config.toml").read()

        self.assertEqual(value_read, fake_model)

    @patch("pathlib.Path")
    @patch("mod.config.handler.ConfigHandler._get_fullpath")
    def test_str(self, mock_path, mock_get_path):
        mock_path = mock_path()

        mock_get_path.return_value = mock_path
        mock_path.__str__.return_value = "config.toml"

        self.assertEqual(ConfigHandler("config.toml").__str__(), "Config: config.toml")

    @patch("pathlib.Path")
    @patch("mod.config.handler.ConfigHandler._get_fullpath")
    def test_repr(self, mock_path, mock_get_path):
        mock_path = mock_path()

        mock_get_path.return_value = mock_path
        mock_path.name = "config.toml"
        mock_path.parent = "directory"

        data = ConfigHandler("config.toml").__repr__()

        self.assertRegex(data, ConfigHandler.__name__)
        self.assertRegex(data, "config.toml",)
        self.assertRegex(data, "directory")
