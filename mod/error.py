"""
    Copyright (c) 2020 - present NekrodNIK, Stepan Skriabin, rus-ai and other.
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
from http import HTTPStatus
from enum import IntEnum


class ServerStatus(IntEnum):
    """Additional server status code and reason phrases
    """
    def __new__(cls, value, phrase, description=''):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.phrase = phrase
        obj.description = description
        return obj

    CLIENT_CLOSED_REQUEST = (499,
                             'Client Closed Request',
                             'Full description: Client Closed Request')
    UNKNOWN_ERROR = (520,
                     'Unknown Error',
                     'Full description: Unknown Error')
    INVALID_SSL_CERTIFICATE = (526,
                               'Invalid SSL Certificate',
                               'Full description: Invalid SSL Certificate')


def check_error_pattern(status: str) -> namedtuple:
    CatchError = namedtuple('CatchError', ['code',
                                           'status',
                                           'detail'])
    try:
        getattr(HTTPStatus, status).value
    except AttributeError:
        http_status_not_found = True
    except TypeError:
        raise TypeError("".join(("Wrong status type passed",
                                 f" it should be {type(str())}",
                                 f" but it was passed {type(status)}")))
    else:
        obj = getattr(HTTPStatus, status)
        http_status_not_found = False

    if http_status_not_found:
        try:
            getattr(ServerStatus, status)
        except AttributeError:
            raise AttributeError("Received a non-existent error status")
        else:
            obj = getattr(ServerStatus, status)

    return CatchError(obj.value,
                      obj.phrase,
                      obj.description)
