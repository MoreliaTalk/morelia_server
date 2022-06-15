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
