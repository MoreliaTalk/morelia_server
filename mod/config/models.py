"""
Copyright (c) 2022 - present NekrodNIK, Stepan Skriabin, rus-ai and other.
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

from pydantic import BaseModel


class DatabaseModel(BaseModel):
    """
    Validation scheme for database field in configuration file.
    """
    url: str = "sqlite:db_sqlite.db"


class HashSizeModel(BaseModel):
    """
    Validation scheme for hash_size field in configuration file.
    """
    size_password: int = 32
    size_auth_id: int = 16


class LoggingModel(BaseModel):
    """
    Validation scheme for logging field in configuration file.
    """
    level: int = 20
    expiration_date: int = 3
    debug_expiration_date: int = 3
    uvicorn_logging_disable: bool = True
    debug: str = "[<b>{time: DD/MM/YY HH:mm:ss}</>]  [<g>{level}</>] " \
                 "{module} | {function} | line:{line: >3} | {message}"
    error: str = "[<b>{time:DD/MM/YY HH:mm:ss}</>]  [<r>{level}</>] " \
                 "{module} | {function} | line:{line: >3} | {message}"
    info: str = "[<b>{time:DD/MM/YY HH:mm:ss}</>]  [<e>{level}</>]  {message}"


class LimitsModel(BaseModel):
    """
    Validation scheme for limits field in configuration file.
    """
    messages: int = 100
    users: int = 100


class ApiModel(BaseModel):
    """
    Validation scheme for api field in configuration file.
    """
    max_version: str = "1.9"
    min_version: str = "1.0"


class ConfigModel(BaseModel):
    """
    Validation scheme for configuration file.
    """

    # Database section
    database: DatabaseModel = DatabaseModel()
    # Hash size section
    hash_size: HashSizeModel = HashSizeModel()
    # Logging section
    logging: LoggingModel = LoggingModel()
    # Server limit section
    limits: LimitsModel = LimitsModel()
    # API version section
    api: ApiModel = ApiModel()
