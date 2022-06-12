import io
from pathlib import PurePath, Path
from unittest import TestCase
from unittest.mock import patch, Mock

import tomli_w

from mod.config import ConfigHandler, ConfigModel


class TestConfigHandler(TestCase):
    @patch("mod.config.handler.Path.is_file", return_value=True)
    def test_get_fullpath_and_check_exist(self, is_file_mock):
        self.assertEqual(ConfigHandler._get_fullpath_and_check_exist(PurePath("config.toml")),
                         Path(PurePath(__file__).parent.parent, "config.toml"))

    @patch("pathlib.Path")
    @patch("mod.config.ConfigHandler._get_fullpath_and_check_exist")
    def test_read(self, MockPath, mock_get_path):
        mock_path = MockPath()

        fake_file = io.StringIO()
        mock_path.open.return_value = fake_file

        fake_toml = ConfigModel().dict()
        fake_file.write(tomli_w.dumps(fake_toml))
        mock_get_path.return_value = mock_path

        value_read = ConfigHandler("config.toml").read()

        self.assertEqual(value_read, fake_toml)

    @patch("pathlib.Path")
    @patch("mod.config.ConfigHandler._get_fullpath_and_check_exist")
    def test_str(self, MockPath, mock_get_path: Mock):
        mock_path = MockPath()

        fake_file = io.StringIO()
        mock_path.open.return_value = fake_file

        fake_toml = ConfigModel().dict()
        fake_file.write(tomli_w.dumps(fake_toml))
        mock_get_path.return_value = mock_path
        mock_get_path().__str__.return_value = "config.toml"

        self.assertRegex(ConfigHandler("config.toml").__str__(), "config.toml")
