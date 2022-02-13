"""
    Copyright (c) 2021 - present NekrodNIK, Stepan Skriabin, rus-ai and other.
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
import configparser
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

from loguru import logger
from collections import namedtuple

from mod.config.validator import DatabaseSection, HashSection


class ConfigNameError(Exception):
    pass


def search_config(file_name: str) -> str:
    sys_name = os.name
    if sys_name == 'nt':
        PurePath = PureWindowsPath
    elif sys_name == 'posix':
        PurePath = PurePosixPath
    else:
        raise "Unknown operation system"

    full_path = Path(__file__)
    for number in range(len(full_path.parents)):
        test_path = PurePath(full_path.parents[number], file_name)
        if Path(test_path).is_file():
            logger.debug(f"Config file found: {test_path}")
            return str(test_path)
    message = """Config file not found,
    please rename example_config.ini to config.ini"""
    logger.error(message)
    raise ConfigNameError(message)


class ConfigHandler:
    def __init__(self, file_name) -> None:
        self.file_path = search_config(file_name)
        self.config = configparser.ConfigParser()

    @staticmethod
    def __validate_database(uri: Any) -> namedtuple:
        result = DatabaseSection(uri=uri)
        Database = namedtuple("Database", ["uri"])
        valid_uri = result.dict()['uri']
        return Database(uri=valid_uri)

    @staticmethod
    def __validate_hash_size(password: Any,
                             auth_id: Any) -> namedtuple:
        result = HashSection(password=password,
                             auth_id=auth_id)
        HashSize = namedtuple("Hash_size", ["password",
                                            "auth_id"])
        valid_password = result.dict()['password']
        valid_auth_id = result.dict()['auth_id']
        return HashSize(password=valid_password,
                        auth_id=valid_auth_id)

    def read(self) -> namedtuple[namedtuple]:
        Config = namedtuple("Config", ["database",
                                       "hash_size",
                                       "logging",
                                       "templates",
                                       "server_limit",
                                       "superuser",
                                       "admin"])
        Database(self.config["DATABASE"].get("uri"))
        HashSize(password=self.config["HASH_SIZE"].get())
        Loself.config['LOGGING']
        TEMPLATES = config["TEMPLATES"]

        SERVER_LIMIT = config["SERVER_LIMIT"]
        SUPERUSER = config["SUPERUSER"]
        ADMIN = config["ADMIN"]
        return Config(database=Database)




if __name__ == "__main__":
    print(search_config("config.ini"))
