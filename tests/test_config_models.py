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

import unittest
from mod.config.models import ConfigModel
from pydantic.error_wrappers import ValidationError

VALID_DICT = {
    'database': {
        'url': 'sqlite:db_sqlite.db'
    },
    'hash_size': {
        'size_password': 32,
        'size_auth_id': 16
    },
    'logging': {
        'level': 20,
        'expiration_date': 3,
        'debug_expiration_date': 3,
        'uvicorn_logging_disable': True,
        'debug': '[<b>{time: DD/MM/YY HH:mm:ss}</>]  [<g>{level}</>] '
                 '{module} | {function} | line:{line: >3} | {message}',
        'error': '[<b>{time:DD/MM/YY HH:mm:ss}</>]  [<r>{level}</>] '
                 '{module} | {function} | line:{line: >3} | {message}',
        'info': '[<b>{time:DD/MM/YY HH:mm:ss}</>]  [<e>{level}</>]  {message}',
    },
    'limits': {'messages': 100, 'users': 100},
    'api': {'max_version': '1.9', 'min_version': '1.0'}
}

INVALID_DICT = {
    'database': {
        'url': 123
    },
    'hash_size': {
        'size_password': 'invalid',
        'size_auth_id': 'invalid'
    },
    'logging': {
        'level': 'invalid',
        'expiration_date': 'invalid',
        'debug_expiration_date': 'invalid',
        'uvicorn_logging_disable': 'invalid',
        'debug': 123,
        'error': 123,
        'info': 123,
    },
    'limits': {'messages': 'invalid', 'users': 'invalid'},
    'api': {'max_version': 123, 'min_version': 123}
}


class TestConfigValidator(unittest.TestCase):
    def test_valid_dict(self) -> None:
        test = ConfigModel.parse_obj(VALID_DICT)

        self.assertEqual(ConfigModel().dict(), VALID_DICT)

    def test_invalid_dict(self) -> None:
        with self.assertRaises(ValidationError):
            ConfigModel.parse_obj(INVALID_DICT)
