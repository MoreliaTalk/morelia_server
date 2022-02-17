"""
    Copyright (c) 2020 - present NekrodNIK, Stepan Skriabin, rus-ai and other.
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

import unittest

from loguru import logger

from mod import error


class TestCheckError(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()

    def setUp(self):
        self.OK = "OK"
        self.WRONG_TYPE_STATUS = 201
        self.UNKNOWN = "UNKNOWN_ERROR"
        self.WRONG_STATUS = "WRONG"

    def tearDown(self):
        del self.OK
        del self.WRONG_TYPE_STATUS
        del self.UNKNOWN
        del self.WRONG_STATUS

    def test_check_HTTPStatus_pattern(self):
        result = error.check_error_pattern(self.OK)
        self.assertEqual(result.code, 200)
        self.assertEqual(result.status, self.OK)

    def test_check_wrong_type_status(self):
        self.assertRaises(TypeError,
                          error.check_error_pattern,
                          self.WRONG_TYPE_STATUS)

    def test_check_wrong_status(self):
        self.assertRaises(AttributeError,
                          error.check_error_pattern,
                          self.WRONG_STATUS)

    def test_check_ServerStatus_pattern(self):
        result = error.check_error_pattern(self.UNKNOWN)
        self.assertEqual(result.code, 520)
        self.assertEqual(result.status, "Unknown Error")
