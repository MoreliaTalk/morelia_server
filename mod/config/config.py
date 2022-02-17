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
from configparser import DuplicateSectionError
from configparser import DuplicateOptionError
from configparser import NoOptionError
from configparser import MissingSectionHeaderError
from configparser import ParsingError
from configparser import Interpolation
from pathlib import Path
from pathlib import PurePath
from time import time
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
        self.config = ConfigParser(interpolation=self._interpolation)
        self.config.read(self.file_path)

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
        message = f"{name} not found"
        logger.error(message)
        raise ConfigNameError(message)

    def _backup_config_file(self) -> tuple[str, PurePath]:
        backup_config_name = "".join((self._name,
                                      ".BAK+",
                                      str(int(time()))))
        file_path = PurePath(self.file_path).parents[0]
        new_config = PurePath(file_path,
                              backup_config_name)
        with open(new_config, "w+") as _file:
            old_config = open(self.file_path, 'r')
            _file.write(old_config.read())
            old_config.close()
            message = f"Backup config.ini to: {new_config}"
        logger.debug(message)
        return message, new_config

    def _validate(self) -> ConfigModel:
        sections = self.config.sections()
        items = [self.config.items(section) for section in sections]
        all_item = []
        for item in items:
            for i in item:
                all_item.append(i)
        kwargs = dict(all_item)
        return ConfigModel(**kwargs)

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
              backup: bool = True) -> str:
        if backup:
            try:
                self._backup_config_file()
            except OSError as err:
                raise BackupConfigError(err)

        section = section.upper()

        if self.config.has_section(section):
            self.config.set(section=section,
                            option=key,
                            value=value)
        else:
            self.config.add_section(section)
            self.config.set(section=section,
                            option=key,
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
            logger.success(f'Write to [{self.file_path}] completed')
            return 'Completed'
