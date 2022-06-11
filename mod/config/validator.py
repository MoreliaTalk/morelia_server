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
    url: str


class HashSizeModel(BaseModel):
    size_password: int
    size_auth_id: int


class LoggingModel(BaseModel):
    level: int
    expiration_date: int
    debug_expiration_date: int
    uvicorn_logging_disable: bool
    debug: str
    error: str
    info: str


class LimitsModel(BaseModel):
    messages: int
    users: int


class ApiModel(BaseModel):
    max_version: str
    min_version: str


class ConfigModel(BaseModel):
    """
    Validation scheme for configuration file.
    """

    class Config:
        """
        Additional configuration for validation scheme.

        Args:
            anystr_strip_whitespace: whether to strip leading and trailing
                                      whitespace for str & byte types
        """

        anystr_strip_whitespace = True

    # Database section
    database: DatabaseModel
    # Hash size section
    hash_size: HashSizeModel
    # Logging section
    logging: LoggingModel
    # Server limit section
    limits: LimitsModel
    # API version section
    api: ApiModel
