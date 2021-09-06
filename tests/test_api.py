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
# above the directory with tests.
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
FIXTURES_PATH = os.path.join(BASE_PATH, 'fixtures')
VALID_JSON = os.path.join(FIXTURES_PATH, 'api.json')
sys.path.append(os.path.split(BASE_PATH)[0])

from mod import api  # noqa


class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()

    def setUp(self):
        self.valid = api.ValidJSON.parse_file(VALID_JSON)

    def tearDown(self):
        del self.valid

    def test_validation_json(self):
        self.assertIsInstance(self.valid.dict(), dict)


if __name__ == "__main__":
    unittest.main()
