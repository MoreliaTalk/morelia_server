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
from pathlib import PurePath

from pydantic import ValidationError
import tomli

from mod.config.models import ConfigModel

PROJECT_ROOT = PurePath(__file__).parent.parent.parent
CONFIG_STANDARD_FILENAME = "config.toml"


class ConfigError(Exception):
    pass


class ConfigNotFoundError(ConfigError):
    pass


class ConfigIsNotValidError(ConfigError):
    pass


def read_config(filepath: str = CONFIG_STANDARD_FILENAME) -> ConfigModel:
    path = Path(filepath)

    if not path.is_absolute():
        path = Path(PROJECT_ROOT, path)

    if not path.is_file():
        raise ConfigNotFoundError()

    raw_config = path.read_text()
    toml_parsed = tomli.loads(raw_config)

    try:
        validated_conf = ConfigModel.parse_obj(toml_parsed)
    except ValidationError:
        raise ConfigIsNotValidError

    return validated_conf
