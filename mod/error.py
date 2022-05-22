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

from enum import IntEnum
from http import HTTPStatus
from typing import NamedTuple


class CatchError(NamedTuple):
    """
    Contains information about error that occurred.
    """
    
    code: int
    status: str
    detail: str


class ServerStatus(IntEnum):
    """
    Additional server status code and reason phrases.

    Notes:
        CLIENT_CLOSED_REQUEST - 499

        VERSION_NOT_SUPPORTED - 505

        UNKNOWN_ERROR - 520

        INVALID_SSL_CERTIFICATE - 526

    """

    def __new__(cls,
                value,
                phrase,
                description=''):
        """
        Optional class constructor.
        """

        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.phrase = phrase
        obj.description = description
        return obj

    CLIENT_CLOSED_REQUEST = (499,
                             'Client Closed Request',
                             'Full description: Client Closed Request')
    VERSION_NOT_SUPPORTED = (505,
                             'Version Not Supported',
                             'Cannot fulfill request')
    UNKNOWN_ERROR = (520,
                     'Unknown Error',
                     'Full description: Unknown Error')
    INVALID_SSL_CERTIFICATE = (526,
                               'Invalid SSL Certificate',
                               'Full description: Invalid SSL Certificate')


def check_error_pattern(status: str) -> CatchError:
    """
    Checks error name against existing error types supported by server.
    The error name is passed as a "status" parameter.

    Args:
        status (str): error name

    Returns:
        (CatchError): named tuple with three value, where

                        ``value`` - status code of error

                        ``phrase`` - status name of error

                        ``description`` - short description of the error

    Raise:
        (AttributeError): raised when an error name is not found among
                          the registered names (in classes ServerStatus and
                          HTTPStatus)
        (TypeError):      raised when Args `status` does not match String type
    """

    try:
        getattr(HTTPStatus, status).value
    except AttributeError:
        try:
            getattr(ServerStatus, status)
        except AttributeError:
            raise AttributeError("Received a non-existent error status")
        else:
            obj = getattr(ServerStatus, status)
            return CatchError(obj.value,
                              obj.phrase,
                              obj.description)
    except TypeError:
        raise TypeError("".join(("Wrong status type passed",
                                 f" it should be {type(str())}",
                                 f" but it was passed {type(status)}")))
    else:
        obj = getattr(HTTPStatus, status)
        return CatchError(obj.value,
                          obj.phrase,
                          obj.description)
