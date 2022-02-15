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
import unittest
from pathlib import PurePath
from loguru import logger

from mod.config.config import ConfigHandler
from mod.config.config import search_config
from mod.config.config import ConfigModel


class TestConfigHandler(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        logger.remove()

    def setUp(self) -> None:
        self.config_name = 'config.ini'
        self.test = ConfigHandler(file_name=self.config_name)

    def tearDown(self) -> None:
        del self.config_name
        del self.test

    def test_search_file(self):
        full_path = search_config(self.config_name)
        result = PurePath(full_path)
        self.assertEqual(result.parts[-1], 'config.ini')

    def test_validate(self):
        valid = self.test._validate()
        result = valid.dict()
        self.assertIsInstance(valid, ConfigModel)
        self.assertEqual(result['password'], 32)
        self.assertTrue(result['uvicorn_logging_disable'])
        self.assertEqual(result['uri'], 'sqlite:db_sqlite.db')
        self.assertEqual(result['folder'], 'templates')

    def test_read(self):
        result = self.test.read()
        self.assertEqual(result.password, 32)
        self.assertTrue(result.uvicorn_logging_disable)
        self.assertEqual(result.uri, 'sqlite:db_sqlite.db')
        self.assertEqual(result.folder, 'templates')

    def test_write(self):
        result = self.test.write(section='DATABASE',
                                 key="URL",
                                 value="URL")
        self.assertEqual(result, 'Completed')
