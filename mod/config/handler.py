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
from pathlib import Path
from pathlib import PurePath

import tomli
from loguru import logger

from mod.config.models import ConfigModel


class ConfigNotFound(Exception):
    pass


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
    _path: Path | None

    def __init__(self,
                 filepath: PurePath | str = "config.toml") -> None:
        self._path = self._get_fullpath_and_check_exist(PurePath(filepath))

    @staticmethod
    def _get_fullpath_and_check_exist(filepath: PurePath) -> Path | None:
        if filepath.is_absolute():
            fullpath = Path(filepath)
        else:
            fullpath = Path(Path(__file__).parent.parent.parent, filepath)

        if fullpath.is_file():
            logger.info("Config found")
            return fullpath
        else:
            logger.warning(f"{fullpath.name} in {fullpath.parent} not found. Default settings are used.")

    def __str__(self) -> str:
        """
        Returned string which contains file path for opened config file.
        """

        return f"Config: {self._path}"

    @staticmethod
    def _parse_and_validate(data: str) -> ConfigModel:
        parsed_conf = tomli.loads(data)
        validated_conf = ConfigModel.parse_obj(parsed_conf)
        return validated_conf

    def read(self) -> ConfigModel:
        """
        Read settings from a configuration file.
        Also, validate settings and generate a named tuple with key=value
        parameters.

        Returns:
            Config: with key=value
        """
        if self._path is not None:
            with self._path.open() as file:
                validated = self._parse_and_validate(file.read())
        else:
            validated = ConfigModel()

        return validated
