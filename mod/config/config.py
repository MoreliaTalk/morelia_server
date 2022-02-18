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

import os

from configparser import ConfigParser
from configparser import DuplicateOptionError
from configparser import ParsingError
from configparser import Interpolation
from pathlib import Path
from pathlib import PurePath
from time import time
from typing import Any
from collections import namedtuple

from loguru import logger

from mod.config.validator import ConfigModel


class NameConfigError(Exception):
    pass


class BackupConfigError(OSError):
    pass


class OperationConfigError(Exception):
    pass


class AccessConfigError(OSError):
    pass


class RebuildConfigError(Exception):
    pass


class CopyConfigError(Exception):
    pass


class ConfigHandler:
    def __init__(self,
                 name: str = 'config.ini',
                 interpolation: Interpolation = None) -> None:
        self._name = str(name)
        self._directory = None
        self._interpolation = interpolation
        self._set_configparser(self._name,
                               self._directory)

    def _set_configparser(self,
                          name: str,
                          directory: Any) -> None:
        self.file_path = self._search_config(name=name,
                                             directory=directory)
        self._config = ConfigParser(interpolation=self._interpolation)
        self._config.read(self.file_path)

    @staticmethod
    def _copy_string(src: str | PurePath,
                     dst: str | PurePath) -> str:
        try:
            with open(dst, "w+") as new_file:
                old_file = open(src, 'r')
                new_file.write(old_file.read())
                old_file.close()
        except OSError as err:
            raise CopyConfigError(err)
        else:
            return "Copied string success"

    def __str__(self) -> str:
        return f"Config: {self.file_path}"

    def __repr__(self) -> str:
        return "".join((f"Class {self.__class__.__name__} with ",
                        f"config_name: {self._name}, ",
                        f"root_directory: {self._directory}, ",
                        f"preprocessed value: {self._interpolation}"))

    @staticmethod
    def _search_config(name: str,
                       directory: Any) -> str:
        full_path = Path(__file__)
        for number in range(len(full_path.parents)):
            if directory is None:
                test_path = PurePath(full_path.parents[number],
                                     name)
            else:
                test_path = PurePath(full_path.parents[number],
                                     directory,
                                     name)
            if Path(test_path).is_file():
                logger.debug(f"Config file found: [{test_path}]")
                return str(test_path)
        message = f"{name} in {test_path} not found"
        logger.error(message)
        raise NameConfigError(message)

    def _backup_config_file(self) -> tuple[str, PurePath]:
        backup_config_name = "".join((self._name,
                                      ".BAK+",
                                      str(int(time()))))
        file_path = PurePath(self.file_path).parents[0]
        new_config = PurePath(file_path,
                              backup_config_name)
        try:
            self._copy_string(src=self.file_path,
                              dst=new_config)
        except CopyConfigError as err:
            os.remove(new_config)
            logger.exception(err)
            raise BackupConfigError(err)
        else:
            message = f"Backup config.ini to: {new_config}"
            logger.debug(message)
            return message, new_config

    def _validate(self) -> ConfigModel:
        sections = self._config.sections()
        items = [self._config.items(section) for section in sections]
        all_item = []
        for item in items:
            for i in item:
                all_item.append(i)
        kwargs = dict(all_item)
        return ConfigModel(**kwargs)

    def _rebuild_config(self,
                        orig_config: str = 'example_config.ini',
                        new_config: str = 'config.ini',
                        directory: str = 'tests/fixtures') -> str:
        try:
            self._copy_string(self._search_config(name=orig_config,
                                                  directory=None),
                              self._search_config(name=new_config,
                                                  directory=directory))
        except CopyConfigError as err:
            logger.exception(err)
            raise RebuildConfigError(err)
        else:
            return 'Config rebuild success'

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

    def read(self) -> namedtuple:
        valid = self._validate().dict()
        valid_dict = valid.copy()
        namedtuple_key = []
        while len(valid) > 0:
            key, _ = valid.popitem()
            namedtuple_key.append(key)
        Config = namedtuple("Config", namedtuple_key)
        return Config(**valid_dict)

    def write(self,
              section: str,
              key: str,
              value: Any,
              backup: bool = True) -> tuple[str, PurePath]:
        if backup:
            backup_info = self._backup_config_file()
        else:
            backup_info = (None, None)

        section = section.upper()
        value = str(value)

        if self._config.has_section(section):
            self._config.set(section=section,
                             option=key,
                             value=value)
        else:
            self._config.add_section(section)
            self._config.set(section=section,
                             option=key,
                             value=value)
        try:
            with open(self.file_path, 'w+') as config_file:
                self._config.write(config_file)
        except (DuplicateOptionError,
                ParsingError) as err:
            logger.debug(err)
            raise OperationConfigError(err)
        except OSError as err:
            logger.debug(err)
            raise AccessConfigError(err)
        else:
            logger.success(f'Write to [{self.file_path}] completed')
            backup_file = backup_info[1]
            return 'Completed', backup_file
