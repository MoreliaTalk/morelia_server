"""
    Copyright (c) 2022 - present NekrodNIK, Stepan Skriabin, rus-ai and other.
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

import os
import stat
import unittest
from pathlib import PurePath
from loguru import logger
from pydantic import ValidationError

from mod.config.config import ConfigHandler
from mod.config.config import AccessConfigError
from mod.config.config import BackupConfigError
from mod.config.config import RebuildConfigError
from mod.config.config import ConfigModel
from mod.config.config import NameConfigError
from mod.config.config import CopyConfigError


class TestConfigHandler(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        logger.remove()

    def setUp(self) -> None:
        self.example_config = 'example_config.ini'
        self.config_name = 'config.ini'
        self.fixtures = 'tests/fixtures'
        self.test = ConfigHandler(directory=self.fixtures)

    def tearDown(self) -> None:
        del self.example_config
        del self.config_name
        del self.fixtures
        del self.test

    def test_set_configparser(self):
        self.test._set_configparser(name=self.config_name,
                                    directory=self.fixtures)
        result = self.test._config.sections()
        self.assertEqual(result[0], "DATABASE")

    def test__str__(self):
        self.assertRegex(str(self.test),
                         'Config:')

    def test__repr__(self):
        result = repr(self.test)
        self.assertRegex(result,
                         "ConfigHandler")
        self.assertRegex(result,
                         self.config_name)

    def test_copy_string(self):
        source = self.test._search_config(name=self.example_config,
                                          directory=None)
        destination = self.test._search_config(name=self.config_name,
                                               directory=self.fixtures)
        result = self.test._copy_string(src=source,
                                        dst=destination)
        self.assertEqual(result, "Copied string success")

    def test_wrong_copy_string(self):
        source = self.test._search_config(name=self.example_config,
                                          directory=None)
        destination = self.test._search_config(name=self.config_name,
                                               directory=self.fixtures)
        # Change mode to not read, not write, not execute to all users
        os.chmod(destination, stat.S_ENFMT)
        self.assertRaises(CopyConfigError,
                          self.test._copy_string,
                          src=source,
                          dst=destination)
        os.chmod(destination, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

    def test_search_config(self):
        full_path = self.test._search_config(self.config_name,
                                             self.fixtures)
        result = PurePath(full_path)
        self.assertIsInstance(result, (str, PurePath))
        self.assertEqual(result.parts[-1], self.config_name)

    def test_wrong_search_config(self):
        self.assertRaises(NameConfigError,
                          self.test._set_configparser,
                          name=self.example_config,
                          directory=self.fixtures)

    def test_backup_file(self):
        result = self.test._backup_config_file()
        self.assertIsInstance(result, tuple)
        self.assertIsInstance(result[0], str)
        self.assertIsInstance(result[1], PurePath)
        self.assertRegex(result[0], "Backup config.ini to:")
        # delete created backup file
        os.remove(result[1])

    def test_wrong_backup_file(self):
        self.test.root_directory = self.fixtures
        destination = self.test._search_config(name=self.config_name,
                                               directory=self.fixtures)
        # Change mode to not read, not write, not execute to all users
        os.chmod(destination, stat.S_ENFMT)
        self.assertRaises(BackupConfigError,
                          self.test._backup_config_file)
        # Change mode to read, write, execute to all users
        os.chmod(destination, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

    def test_validate(self):
        valid = self.test._validate()
        result = valid.dict()
        self.assertIsInstance(valid, ConfigModel)
        self.assertEqual(result['size_password'], 32)
        self.assertTrue(result['uvicorn_logging_disable'])
        self.assertEqual(result['uri'], 'sqlite:db_sqlite.db')
        self.assertEqual(result['folder'], 'templates')

    def test_rebuild_config(self):
        result = self.test._rebuild_config()
        self.assertEqual(result, 'Config rebuild success')

    def test_wrong_rebuild_config(self):
        destination = self.test._search_config(name=self.config_name,
                                               directory=self.fixtures)
        # Change mode to not read, not write, not execute to all users
        os.chmod(destination, stat.S_ENFMT)
        self.assertRaises(RebuildConfigError,
                          self.test._rebuild_config)
        # Change mode to read, write, execute to all users
        os.chmod(destination, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

    def test_get_root_directory(self):
        directory = self.test.root_directory
        self.assertEqual(directory, self.fixtures)

    def test_set_root_directory(self):
        self.test.root_directory = self.fixtures
        result = PurePath(self.test.file_path)
        self.assertEqual(result.parts[-1], self.config_name)
        self.assertEqual(result.parts[-2], 'fixtures')
        self.assertEqual(result.parts[-3], 'tests')

    def test_get_config_name(self):
        result = self.test.config_name
        self.assertEqual(result, self.config_name)

    def test_set_config_name(self):
        result = self.test.config_name = 'blank_setup.cfg'
        self.assertEqual(result, 'blank_setup.cfg')

    def test_read(self):
        result = self.test.read()
        self.assertEqual(result.size_password, 32)
        self.assertTrue(result.uvicorn_logging_disable)
        self.assertEqual(result.uri, 'sqlite:db_sqlite.db')
        self.assertEqual(result.folder, 'templates')

    def test_wrong_read(self):
        self.test.root_directory = self.fixtures
        self.test.config_name = 'wrong_config.ini'
        self.assertRaises(ValidationError,
                          self.test.read)

    def test_write_without_backup(self):
        self.test.root_directory = self.fixtures
        result = self.test.write(section='database',
                                 key="url",
                                 value="www.test.ru",
                                 backup=False)
        self.assertEqual(result[0], 'Completed')
        self.assertEqual(result[1], None)
        # rebuild config.ini to tests
        self.test._rebuild_config()

    def test_write_with_backup(self):
        self.test.root_directory = self.fixtures
        result = self.test.write(section='database',
                                 key="url",
                                 value="www.test.ru",
                                 backup=True)
        self.assertEqual(result[0], 'Completed')
        self.assertRegex(PurePath(result[1]).parts[-1],
                         'config.ini.BAK+')
        # rebuild config.ini to tests
        self.test._rebuild_config()
        # delete created backup file
        os.remove(result[1])

    def test_write_with_access_error(self):
        self.test.root_directory = self.fixtures
        self.test.config_name = self.config_name
        destination = self.test._search_config(name=self.config_name,
                                               directory=self.fixtures)
        # Change mode to not read, not write, not execute to all users
        os.chmod(destination, stat.S_ENFMT)
        self.assertRaises(AccessConfigError,
                          self.test.write,
                          section='database',
                          key="url",
                          value="www.test.ru",
                          backup=False)
        # Change mode to read, write, execute to all users
        os.chmod(destination, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        # rebuild config.ini to tests
        self.test._rebuild_config()
