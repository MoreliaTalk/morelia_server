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
from configparser import ConfigParser
from configparser import DuplicateSectionError
from configparser import DuplicateOptionError
from configparser import NoOptionError
from configparser import MissingSectionHeaderError
from configparser import ParsingError
import os
from pathlib import Path
from pathlib import PurePosixPath
from pathlib import PureWindowsPath
from typing import Any
from collections import namedtuple

from loguru import logger


from mod.config.validator import ConfigModel


class ConfigNameError(Exception):
    pass


class BackupConfigError(OSError):
    pass


class ConfigOperationError(Exception):
    pass


class ConfigAccessError(OSError):
    pass


class ConfigHandler:
    def __init__(self,
                 name: str = 'config.ini') -> None:
        self._name = str(name)
        self._directory = None
        self._set_configparser(self._name,
                               self._directory)

    def _search_config(self,
                       name: str,
                       directory: Any) -> str:
        sys_name = os.name
        if sys_name == 'nt':
            PurePath = PureWindowsPath
        elif sys_name == 'posix':
            PurePath = PurePosixPath
        else:
            message = "Unknown operation system"
            logger.exception(message)
            raise Exception(message)
        full_path = Path(__file__)
        for number in range(len(full_path.parents)):
            if directory is not None:
                test_path = PurePath(full_path.parents[number],
                                     directory,
                                     name)
            else:
                test_path = PurePath(full_path.parents[number],
                                     name)
            if Path(test_path).is_file():
                logger.debug(f"Config file found: {test_path}")
                return str(test_path)
        message = """Config file not found,
        please rename example_config.ini to config.ini"""
        logger.error(message)
        raise ConfigNameError(message)

    def _set_configparser(self,
                          name: str,
                          directory: Any) -> None:
        self.file_path = self._search_config(name=name,
                                             directory=directory)
        self.config = ConfigParser(interpolation=None)
        self.config.read(self.file_path)

    def __str__(self) -> str:
        return f"Config: {self.file_path}"

    def __repr__(self) -> str:
        return "".join((f"Class {self.__class__.__name__} with ",
                        f"config_name: {self._name}, ",
                        f"root_directory: {self._directory}"))

    @property
    def root_directory(self) -> str:
        return self._directory

    @root_directory.setter
    def root_directory(self,
                       name: str) -> None:
        if name:
            self._directory = str(name)
            self._set_configparser(name=self._name,
                                   directory=self._directory)

    @property
    def config_name(self) -> str:
        return self._name

    @config_name.setter
    def config_name(self,
                    name: str) -> None:
        if name:
            self._name = str(name)
            self._set_configparser(name=self._name,
                                   directory=self._directory)

    def _validate(self) -> ConfigModel:
        sections = self.config.sections()
        items = [self.config.items(section) for section in sections]
        all_item = []
        for item in items:
            for i in item:
                all_item.append(i)
        kwargs = dict(all_item)
        return ConfigModel(**kwargs)

    def read(self) -> namedtuple:
        valid = self._validate().dict()
        valid_dict = valid.copy()
        namedtuple_key = []
        while len(valid) > 0:
            key, _ = valid.popitem()
            namedtuple_key.append(key)
        Config = namedtuple("Config", namedtuple_key)
        return Config(**valid_dict)

    def _backup_file(self) -> str:
        try:
            filename = None
            message = f"Backup config file to: {filename}"
            logger.debug(message)
            return message
        except OSError as err:
            message = f"{err}"
            logger.exception(message)
            raise BackupConfigError(message)

    def write(self,
              section: str,
              key: str,
              value: Any):

        self._backup_file()
        if self.config.has_section(section):
            self.config.set(section=section.capitalize(),
                            option=key.capitalize(),
                            value=value)
        else:
            self.config.add_section(section)
            self.config.set(section=section.capitalize(),
                            option=key.capitalize(),
                            value=value)
        try:
            with open(self.file_path, 'w+') as config_file:
                self.config.write(config_file)
        except (DuplicateSectionError,
                DuplicateOptionError,
                NoOptionError,
                MissingSectionHeaderError,
                ParsingError) as err:
            logger.debug(err)
            raise ConfigOperationError(err)
        except OSError as err:
            logger.debug(err)
            raise ConfigAccessError(err)
        else:
            logger.success('Completed')
            return 'Completed'
