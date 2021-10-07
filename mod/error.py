"""
    Copyright (c) 2020 - present NekrodNIK, Stepan Skriabin, rus-ai and other.
    Look at the file AUTHORS.md(located at the root of the project) to get the full list.

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
from http import HTTPStatus
from enum import Enum, IntEnum


class ServerStatus(IntEnum):
    """Server status code and reason phrases

    Args:
        enum ([type]): [description]
    """
    def __new__(cls, value, phrase, description=''):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.phrase = phrase
        obj.description = description
        return obj

    CLIENT_CLOSED_REQUEST = 499, 'Client Closed Request', 'Client Closed Request'
    UNKNOWN_ERROR = 520, 'Unknown Error1', 'Unknown Error2'
    INVALID_SSL_CERTIFICATE = 526, 'Invalid SSL Certificate', 'Invalid SSL Certificate'


def check_error_pattern(status: str) -> Enum:
    try:
        code = getattr(HTTPStatus, status).value
    except AttributeError:
        code = getattr(ServerStatus, status).value
        status = getattr(ServerStatus, status).phrase
        description = getattr(ServerStatus, status).description
    else:
        status = getattr(HTTPStatus, status).phrase
        description = getattr(HTTPStatus, status).description
    return Enum("Error", {"code": code,
                          "status": status,
                          "detail": description})
