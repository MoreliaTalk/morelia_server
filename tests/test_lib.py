"""
    Copyright (c) 2020 - present NekrodNIK, Stepan Scryabin, rus-ai and other.
    Look at the file AUTHORS.md(located at the root of the project) to get the full list.

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
import sys
import unittest

from loguru import logger

# Add path to directory with code being checked
# to variable 'PATH' to import modules from directory
# above the directory with the tests.
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.split(BASE_PATH)[0])
from mod import lib  # noqa


class TestHash(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()

    def setUp(self):
        self.password = 'password'
        self.salt = b'salt'
        self.key = b'key'
        self.uuid = 123456
        self.generator = lib.Hash(self.password,
                                  self.uuid,
                                  self.salt,
                                  self.key)
        self.hash_password = self.generator.password_hash()

    def tearDown(self):
        del self.generator
        del self.hash_password
        del self.password
        del self.salt
        del self.key
        del self.uuid

    def test_check_str_in_result(self):
        self.assertIsInstance(self.generator.password_hash(),
                              str)

    def test_check_space_password(self):
        self.password = ' '
        self.generator = lib.Hash(self.password,
                                  self.uuid,
                                  self.salt)
        self.assertIsInstance(self.generator.password_hash(),
                              str)

    def test_check_256_symbols_password(self):
        self.password = '8b915f2f0b0d0ccf27854dd708524d0b\
                         5a91bdcd3775c6d3335f63d015a43ce1'
        self.generator = lib.Hash(self.password,
                                  self.uuid,
                                  self.salt)
        self.assertIsInstance(self.generator.password_hash(),
                              str)

    def test_check_wrong_password_type(self):
        self.password = 123456789
        self.assertRaises(AttributeError,
                          lib.Hash,
                          self.password,
                          self.uuid,
                          self.salt)

    def test_wrong_hash_password_type(self):
        self.hash_password = 123456789
        generator = lib.Hash(self.password,
                             self.uuid,
                             self.salt,
                             hash_password=self.hash_password)
        self.assertRaises(TypeError,
                          generator.check_password)

    def test_check_password(self):
        self.new_generator = lib.Hash(self.password,
                                      self.uuid,
                                      self.salt,
                                      self.key,
                                      hash_password=self.hash_password)
        self.assertTrue(self.new_generator.check_password())

    def test_check_auth_id(self):
        self.assertIsInstance(self.generator.auth_id(),
                              str)


if __name__ == "__main__":
    unittest.main()
