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
from unittest.mock import patch, Mock

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
        self.assertEqual(ConfigHandler._get_fullpath(PurePath("config.ini")),
                         Path(PurePath(__file__).parent.parent, "config.ini"))

    @patch("mod.config.handler.ConfigHandler._get_fullpath")
    def test_read(self, mock_get_path):
        model = ConfigModel()
        in_file = IniParser.dumps(model.dict())

        mock_get_path().open().__enter__().read.return_value = in_file

        value_read = ConfigHandler("config.ini").read()
        self.assertEqual(value_read, model)

    @patch("mod.config.handler.ConfigHandler._get_fullpath")
    def test_write(self, mock_get_path):
        model = ConfigModel()
        expected_data = IniParser.dumps(model.dict())

        ConfigHandler("config.ini").write(model, backup=False)
        write_data = mock_get_path().open().__enter__().write.call_args[0][0]

        self.assertEqual(write_data, expected_data)

    @patch("builtins.open")
    @patch("mod.config.handler.ConfigHandler.read")
    @patch("mod.config.handler.ConfigHandler._get_fullpath")
    def test_backup(self, _, mock_cfg_read, mock_open):
        model = ConfigModel()
        in_config_file = IniParser.dumps(model.dict())

        mock_cfg_read.return_value = model
        ConfigHandler("config.ini").backup("new_backup")

        backup_write_data = mock_open().__enter__().write.call_args[0][0]
        self.assertEqual(backup_write_data, in_config_file)

    @patch("mod.config.handler.Path")
    @patch("mod.config.handler.ConfigHandler._write_raw")
    @patch("mod.config.handler.ConfigHandler._get_fullpath")
    def test_restore(self, _, mock_write_raw, mock_path):
        in_backup_data = IniParser.dumps(ConfigModel().dict())

        mock_path().open().__enter__().read.return_value = in_backup_data

        ConfigHandler("config.ini").restore("new_backup")

        self.assertEqual(mock_write_raw.call_args[0][0], in_backup_data)

    @patch("pathlib.Path")
    @patch("mod.config.handler.ConfigHandler._get_fullpath")
    def test_str(self, mock_path, mock_get_path):
        mock_path = mock_path()

        mock_get_path.return_value = mock_path
        mock_path.__str__.return_value = "config.ini"

        self.assertEqual(ConfigHandler("config.ini").__str__(), "Config: config.ini")

    @patch("pathlib.Path")
    @patch("mod.config.handler.ConfigHandler._get_fullpath")
    def test_repr(self, mock_path, mock_get_path):
        mock_path = mock_path()

        mock_get_path.return_value = mock_path
        mock_path.name = "config.ini"
        mock_path.parent = "directory"

        data = ConfigHandler("config.ini").__repr__()

        self.assertRegex(data, ConfigHandler.__name__)
        self.assertRegex(data, "config.ini")
        self.assertRegex(data, "directory")
