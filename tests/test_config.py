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
import unittest
from pathlib import PurePath
from loguru import logger

from mod.config.config import ConfigHandler
from mod.config.config import ConfigModel
from mod.lib import rebuild_config


class TestConfigHandler(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        logger.remove()

    def setUp(self) -> None:
        self.config_name = 'config.ini'
        self.test = ConfigHandler()

    def tearDown(self) -> None:
        del self.config_name
        del self.test

    def test__str__(self):
        self.assertRegex(str(self.test),
                         'Config:')

    def test__repr__(self):
        result = repr(self.test)
        self.assertRegex(result,
                         "ConfigHandler")
        self.assertRegex(result,
                         self.config_name)

    def test_set_configparser(self):
        self.test._set_configparser(self.config_name,
                                    None)
        result = self.test.config.sections()
        self.assertEqual(result[0], "DATABASE")

    def test_search_file(self):
        full_path = self.test._search_config(self.config_name,
                                             None)
        result = PurePath(full_path)
        self.assertEqual(result.parts[-1], 'config.ini')

    def test_backup_file(self):
        result = self.test._backup_config_file()
        self.assertIsInstance(result, tuple)
        self.assertIsInstance(result[0], str)
        self.assertIsInstance(result[1], PurePath)
        self.assertRegex(result[0], "Backup config.ini to:")
        # delete created backup file
        os.remove(result[1])

    def test_validate(self):
        valid = self.test._validate()
        result = valid.dict()
        self.assertIsInstance(valid, ConfigModel)
        self.assertEqual(result['password'], 32)
        self.assertTrue(result['uvicorn_logging_disable'])
        self.assertEqual(result['uri'], 'sqlite:db_sqlite.db')
        self.assertEqual(result['folder'], 'templates')

    def test_get_root_directory(self):
        directory = self.test.root_directory
        self.assertEqual(directory, None)

    def test_set_root_directory(self):
        new_root_directory = 'tests'
        self.test.root_directory = new_root_directory
        result = PurePath(self.test.file_path)
        self.assertEqual(result.parts[-1], "config.ini")
        self.assertEqual(result.parts[-2], new_root_directory)

    def test_get_config_name(self):
        result = self.test.config_name
        self.assertEqual(result, self.config_name)

    def test_set_config_name(self):
        result = self.test.config_name = 'setup.cfg'
        self.assertEqual(result, 'setup.cfg')

    def test_read(self):
        result = self.test.read()
        self.assertEqual(result.password, 32)
        self.assertTrue(result.uvicorn_logging_disable)
        self.assertEqual(result.uri, 'sqlite:db_sqlite.db')
        self.assertEqual(result.folder, 'templates')

    def test_write(self):
        self.test.root_directory = './tests'
        result = self.test.write(section='database',
                                 key="url",
                                 value="www.test.ru",
                                 backup=False)
        self.assertEqual(result, 'Completed')
        # rebuild config.ini to tests
        rebuild_config()
