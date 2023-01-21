"""
Copyright (c) 2021 - present MoreliaTalk team and other.
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

from loguru import logger
from pydantic import ValidationError
import tomli

from const import ROOT_DIR
from mod.config.models import ConfigModel

CONFIG_STANDARD_FILENAME = "config.toml"


def read_config(filepath: str = CONFIG_STANDARD_FILENAME) -> ConfigModel:
    path = Path(filepath)

    if not path.is_absolute():
        path = Path(ROOT_DIR, path)

    if path.is_file():
        raw_config = path.read_text()
        toml_parsed = tomli.loads(raw_config)

        try:
            config_option = ConfigModel.parse_obj(toml_parsed)
            logger.success(f"Config {path.name} in {path.parent} successful read")
        except ValidationError:
            logger.error(f"Config {path.name} in {path.parent} not valid."
                         f"Default settings are used.")

            config_option = ConfigModel()

    else:
        logger.warning(f"Config {path.name} in {path.parent} not found."
                       f"Default settings are used.")

        config_option = ConfigModel()

    return config_option
