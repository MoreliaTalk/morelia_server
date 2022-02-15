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


def search_config(file_name: str) -> str:
    sys_name = os.name
    if sys_name == 'nt':
        PurePath = PureWindowsPath
    elif sys_name == 'posix':
        PurePath = PurePosixPath
    else:
        raise Exception("Unknown operation system")

    full_path = Path(__file__)
    for number in range(len(full_path.parents)):
        test_path = PurePath(full_path.parents[number],
                             file_name)
        if Path(test_path).is_file():
            logger.debug(f"Config file found: {test_path}")
            return str(test_path)
    message = """Config file not found,
    please rename example_config.ini to config.ini"""
    logger.error(message)
    raise ConfigNameError(message)


class ConfigHandler:
    def __init__(self,
                 file_name: str) -> None:
        self.file_path = search_config(file_name)
        self.config = ConfigParser(interpolation=None)
        self.config.read(self.file_path)

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

    def write(self,
              section: str,
              key: str,
              value: Any):
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
        except DuplicateSectionError as err:
            pass
        except DuplicateOptionError as err:
            pass
        except NoOptionError as err:
            pass
        except MissingSectionHeaderError as err:
            pass
        except ParsingError as err:
            pass
        except OSError as err:
            pass
        else:
            logger.success('Completed')
            return 'Completed'
