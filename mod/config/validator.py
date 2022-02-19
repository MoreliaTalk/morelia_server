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


class ConfigModel(BaseModel):
    """
    Describe the validation scheme for config.ini file which contain all
    server settings.
    """

    class Config:
        """
        Additional configuration for validation scheme.

        Args:
            anystr_strip_whitespace (bool): whether to strip leading and
                trailing whitespace for str & byte types
        """

        anystr_strip_whitespace = True

    # Database section
    uri: str
    # Hash size section
    password: str
    auth_id: int
    # Logging section
    level: int
    expiration_date: int
    debug_expiration_date: int
    uvicorn_logging_disable: bool
    debug: str
    error: str
    info: str
    # Templates section
    folder: str
    # Server limit section
    messages: int
    users: int
    # Admin section
    secret_key: str
