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
from fastapi import Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login import LoginManager
from starlette.responses import HTMLResponse

from mod import lib
from mod.config.config import ConfigHandler
from mod.db.dbhandler import DBHandler


config = ConfigHandler()
config_option = config.read()

db_connect = DBHandler(config_option.uri)

router = APIRouter()


class NotAuthenticatedException(Exception):
    """
    Occurs when the user's authorization data is missing or incorrect.
    """


login_manager = LoginManager(config_option.secret_key,
                             token_url="/login/token",
                             use_cookie=True,
                             use_header=False)

login_manager.not_authenticated_exception = NotAuthenticatedException


@login_manager.user_loader()  # type: ignore
def get_admin_user_data(username: str):
    """
    Requesting data from the database and checking it against the username.

    Args:
        username: username admin user

    Returns:
        admin user data from db
    """

    data = db_connect.get_admin_by_name(username=username)
    if data.count():
        return data[0]


@router.post("/login/token")
def login_token(data: OAuth2PasswordRequestForm = Depends()):
    """
    Returns a response that contains the admin token, valid for 15 minutes.

    Args:
        data: login data

    Returns:
        response with cookies embedded in it
    """

    admin_user_data_db = get_admin_user_data(data.username)
    if not admin_user_data_db:
        return HTMLResponse("""<script>
                            window.document.location.href = "./"
                            </script>""")

    generator = lib.Hash(data.password,
                         admin_user_data_db.id,
                         hash_password=admin_user_data_db.hashPassword,
                         key=b"key",
                         salt=b"salt")
    if not generator.check_password():
        return HTMLResponse("""<script>
                            window.document.location.href = "./"
                            </script>""")

    token = login_manager.create_access_token(data={"sub": data.username})

    response = HTMLResponse("""<script>
                            window.document.location.href = "../"
                            </script>""")

    login_manager.set_cookie(response,
                             token)

    return response


@router.post("/login/logout")
def logout(request: Request):
    """
    Returns a response that contains the invalid admin token.

    Args:
        request: request for server

    Returns:
        response with cookies embedded in it
    """

    incorrect_token = "MoreliaTalk"

    response = HTMLResponse("""<script>
                            window.document.location.href = "../"
                            </script>""")

    login_manager.set_cookie(response,
                             incorrect_token)

    return response
