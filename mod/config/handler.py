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
import io
import logging
from pathlib import Path
from pathlib import PurePath
from time import time

from loguru import logger
import pydantic

from mod.config.models import ConfigModel


class IniParser:
    """
    This class a layer for conveniently converting dict \
    to string in .ini file format and back using ConfigParser.
    """

    @staticmethod
    def loads(data: str) -> dict:
        """
        Converts a string in .ini format to a parsed dict
        Args:
            data(str): .ini string

        Returns:
            dict: parsed object
        """
        parser = configparser.ConfigParser()
        parser.read_string(data)
        return dict(parser)

    @staticmethod
    def dumps(data: dict) -> str:
        """
        Converts a dict to string in .ini format
        Args:
            data(str): any dict

        Returns:
            dict: .ini string
        """
        io_string = io.StringIO()
        parser = configparser.ConfigParser()

        parser.read_dict(data)
        parser.write(io_string)

        return io_string.read()


class ConfigNotExistError(Exception):
    pass


class ConfigBackupNotFoundError(Exception):
    pass


class ConfigHandler:
    """
    Class for work with settings contains in configuration file.
    By default, it is config.ini

    Args:
        filepath(PurePath | str): absolute or relative path to file
        log: Disable/enable logger from loguru, default True.
    """
    _path: Path
    _is_exist: bool

    def __init__(self,
                 filepath: PurePath | str = "config.ini",
                 log: bool = True) -> None:
        if log is False:
            logger.remove()

        self._path = self._get_fullpath(PurePath(filepath))
        self._check_exist()

    @staticmethod
    def _get_fullpath(filepath: PurePath) -> Path:
        """
        Returns the full absolute path to the file,
        depending on whether the path given for input is absolute.
        Args:
            filepath(PurePath): relative or absolute path to file

        Returns:

        """
        if filepath.is_absolute():
            return Path(filepath)
        else:
            return Path(PurePath(__file__).parent.parent.parent, filepath)

    def _check_exist(self) -> None:
        if self._path.is_file():
            logger.info("Config found")
            self._is_exist = True
        else:
            logger.info(f"{self._path.name} in {self._path.parent} not found. "
                        f"Default settings are used.")
            self._is_exist = False

    def _parse_and_validate(self, data: str) -> ConfigModel:
        try:
            validated_conf = ConfigModel.parse_obj(IniParser.loads(data))
        except pydantic.ValidationError:
            logging.error(f"Config {self._path} is not valid. "
                          f"Default settings are used.")
            validated_conf = ConfigModel()

        return validated_conf

    def read(self) -> ConfigModel:
        """
        Read settings from a configuration file.
        Also, validate settings and generate a named tuple with key=value
        parameters.

        Returns:
            Config: with key=value
        """
        if self._is_exist:
            with self._path.open() as file:
                validated = self._parse_and_validate(file.read())
        else:
            validated = ConfigModel()

        return validated

    def _write_raw(self, data: str):
        with self._path.open("w") as file:
            file.write(data)

        if not self._is_exist:
            self._is_exist = True

    def write(self, data: ConfigModel, backup: bool = True) -> None:
        if backup:
            self.backup("".join((str(self._path), ".BAK+", str(time()))))

        self._write_raw(IniParser.dumps(data.dict()))

    def backup(self, backup_name: str) -> None:
        data = self.read()

        with open(backup_name, "w") as file:
            file.write(IniParser.dumps(data.dict()))

    def restore(self, backup_name: str = None) -> None:
        if backup_name is None:
            data = IniParser.dumps(ConfigModel().dict())
        else:
            if Path(backup_name).is_file():
                with self._path.open() as file:
                    data = file.read()
            else:
                raise ConfigBackupNotFoundError()

        self._write_raw(data)

    def __str__(self) -> str:
        """
        Returned string which contains file path for opened config file.
        """

        return f"Config: {self._path}"

    def __repr__(self) -> str:
        """
        Returned name of created class and parameters send to class object.
        """

        return "".join((f"Class {self.__class__.__name__} with ",
                        f"config_name= {self._path.name}, ",
                        f"config_directory= {self._path.parent}"))
