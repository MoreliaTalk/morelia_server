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

from collections import namedtuple
from configparser import ConfigParser
from configparser import Interpolation
import os
from pathlib import Path
from pathlib import PurePath
from time import time
from typing import Any
from typing import Optional
from typing import Tuple

from loguru import logger

from mod.config.validator import ConfigModel


class NameConfigError(Exception):
    """
    Occurs when there is an error in the name of the file.
    For example there is no such file at all.
    """


class BackupConfigError(OSError):
    """
    Occurs when a backup of a file is impossible.
    For example, you can't read the original settings file,
    or you don't have written access to the directory.
    """


class OperationConfigError(Exception):
    """
    Occurs when an option written to a configuration file is duplicated.
    Or when a configuration file parsing error has occurred.
    """


class AccessConfigError(OSError):
    """
    Occurs when writing to the configuration file failed.
    Because of the lack of write permissions to the file
    or the lack of the file itself.
    """


class RebuildConfigError(Exception):
    """
    Occurs when the configuration file could not be restored.
    Because of the lack of permissions to write to the file
    or the absence of the file itself.
    """


class CopyConfigError(Exception):
    """
    Occurs when it was not possible to copy old configuration file to new one.
    Because there are no write permissions to the file or because the file
    itself is missing.
    """


class ConfigHandler:
    """
    Main module for work with settings contains in configuration file.
    By default, it is config.ini

    Args:
        name: name of configuration file.
        interpolation: Interpolation behaviour may be customized by providing
                       a custom handler through the interpolation argument,
                       by default it is BasicInterpolation. None can be used to
                       turn off interpolation completely, ExtendedInterpolation
                       provides a more advanced variant inspired by
                       zc.buildout. More on the subject in the dedicated
                       documentation section for build-ins configparser
                       modules.
        log: Disable/enable logger from loguru, default True.
    """
    _directory: Optional[str]

    def __init__(self,
                 directory: Optional[str] = None,
                 name: Optional[str] = "config.ini",
                 interpolation: Interpolation = None) -> None:
        self._name = str(name)
        self._directory = directory
        self._interpolation = interpolation
        self._set_configparser(self._name,
                               self._directory)

    def _set_configparser(self,
                          name: str,
                          directory: Any) -> None:
        """
        Starts the process of finding a configuration file.
        Configures configparser module to work with it.

        Args:
            name: name of configuration file
            directory: directory name which contain configuration file, e.g.
                       tests/fixtures
        """

        self.file_path = self._search_config(name=name,
                                             directory=directory)
        self._config = ConfigParser(interpolation=self._interpolation)
        self._config.read(self.file_path)

    @staticmethod
    def _copy_string(src: str | PurePath,
                     dst: str | PurePath) -> str:
        """
        Copies data line by line from one file to another.

        Args:
            src: source file path
            dst: destination file path

        Returns:
            "Copied string success" message

        Raises:
            CopyConfigError: no write permissions to the file or because
                             the file itself is missing.
        """

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
        """
        Returned string which contains file path for opened config file.
        """

        return f"Config: {self.file_path}"

    def __repr__(self) -> str:
        """
        Returned name of created class and parameters send to class object.
        """

        return "".join((f"Class {self.__class__.__name__} with ",
                        f"config_name= {self._name}, ",
                        f"root_directory= {self._directory}, ",
                        f"preprocessed value= {self._interpolation}"))

    @staticmethod
    def _search_config(name: str,
                       directory: Any) -> str:
        """
        Searching config file and create full path to it.

        Args:
            name: name of configuration file
            directory: directory name which contain configuration file, e.g.
                       tests/fixtures

        Returns:
            /path/to/config/file/config.ini

        Raises:
            NameConfigError: no such a file.
        """

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
                return str(test_path)

    def _backup_config_file(self) -> tuple[str, PurePath]:
        """
        Creating a backup copy of the configuration file.
        
        Also, addition at the end of the name this string: BAK + Unix time.

        Returns:
            tuple: contains string 'Backup config.ini to /path/to/config/file'
                   and path-like file object.

        Raises:
            BackupConfigError: can't read the original settings file, or you
                               don't have written access to the directory.
        """

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
        """
        Read and validate the parameters contained in the configuration file.

        Returns:
            pydantic model (ConfigModel) which contains all validated
            parameters
        """

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
        """
        Restoring the configuration file.
        Copying lines from example_config.ini to config.ini file.

        Args:
            orig_config: default 'example_config.ini'
            new_config: default 'config.ini'
            directory: default 'tests/fixtures'

        Returns:
            "Config rebuild success" message

        Raises:
            RebuildConfigError: the lack of permissions to write to file
                                or the absence of file itself
        """

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
    def root_directory(self) -> str | None:
        """
        Reports name of directory that is set for initial search config file.

        Returns:
            name of directory, if None that mean root directory corresponds
            to the main (uppermost) project directory
        """

        return self._directory

    @root_directory.setter
    def root_directory(self,
                       name: str) -> None:
        """
        Sets a new name for the root directory.

        Args:
            name: new name root directory
        """

        self._directory = str(name)
        self._set_configparser(name=self._name,
                               directory=self._directory)

    @property
    def config_name(self) -> str:
        """
        Parameter that reports name of configuration file.

        Returns:
            name of configuration file
        """

        return self._name

    @config_name.setter
    def config_name(self,
                    name: str) -> None:
        """
        Sets of new name for configuration file.

        Args:
            name: new name for configuration file
        """

        self._name = str(name)
        self._set_configparser(name=self._name,
                               directory=self._directory)

    def read(self) -> Any:
        """
        Read settings from a configuration file.
        Also, validate settings and generate a named tuple with key=value
        parameters.

        Returns:
            Config: with key=value
        """

        valid = self._validate().dict()
        valid_dict = valid.copy()
        namedtuple_key = []
        while len(valid) > 0:
            key, _ = valid.popitem()
            namedtuple_key.append(key)

        Config = namedtuple("Config", namedtuple_key)  # type: ignore
        return Config(**valid_dict)  # type: ignore

    def write(self,
              section: str,
              key: str,
              value: Any,
              backup: bool = True) -> tuple[str, PurePath | None]:
        """
        Writing new settings to the server configuration file.
        The backup option is used to select whether to save the previous
        settings to a special file or not.

        Args:
            section:  each led by a [section] header
            key: name of parameters
            value: value of parameters, auto converted to string object
            backup: save or not previous settings, default True

        Returns:
            tuple which contain string 'Completed' and path-like object with
            backup file link or None if set backup is False

        Raises:
            AccessConfigError: lack of write permissions to the file or
                               the lack of the file itself
        """

        backup_info: Tuple[Optional[str], Optional[PurePath]]

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
        except OSError as err:
            logger.debug(err)
            raise AccessConfigError(err)
        else:
            logger.success(f'Write to [{self.file_path}] completed')
            backup_file = backup_info[1]
            return 'Completed', backup_file
