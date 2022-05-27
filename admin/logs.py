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

from fastapi import APIRouter
from fastapi import Depends
from fastapi.requests import Request

from admin import login

router = APIRouter()

log_string = str()


@router.get("/logs/get")
def get_logs(request: Request,
             user=Depends(login.login_manager)):
    """
    Returns a dict with server logs.

    Args:
        request: request to the server
        user: user authentication check

    Returns:
        (dict)
    """

    return {"logs": log_string}


def loguru_handler(log: str):
    """
    Function collects server logs.

    Args:
        log: new log string
    """

    global log_string
    log_string += log
