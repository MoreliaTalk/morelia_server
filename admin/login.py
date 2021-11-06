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

from pathlib import Path
from loguru import logger

from fastapi import APIRouter, Depends, Request
from fastapi_login import LoginManager
from fastapi.security import OAuth2PasswordRequestForm

from configparser import ConfigParser

from starlette.responses import HTMLResponse
from mod.db import models
from mod import lib
import sqlobject as orm

config = ConfigParser()
config.read(Path(__file__).parent.parent / "config.ini")

SECRET_KEY = config["ADMIN"].get("SECRET_KEY")

database = config["DATABASE"]

try:
    db_connection = orm.connectionForURI(database.get("uri"))
except Exception as ERROR:
    logger.exception(str(ERROR))
finally:
    orm.sqlhub.processConnection = db_connection

router = APIRouter()


class NotAuthenticatedException(Exception):
    pass


login_manager = LoginManager(
    SECRET_KEY,
    token_url="/login/token",
    use_cookie=True,
    use_header=False
)

login_manager.not_authenticated_exception = NotAuthenticatedException


@login_manager.user_loader()
def get_admin_user_data(username: str):
    data = models.Admin.selectBy(username=username)
    if data.count():
        return data[0]


@router.post("/login/token")
def login_token(data: OAuth2PasswordRequestForm = Depends()):
    admin_user_data_db = get_admin_user_data(data.username)
    if not admin_user_data_db:
        return HTMLResponse(
            """
            <script>
            window.document.location.href = "./"
            </script>
            """
        )

    generator = lib.Hash(
        data.password,
        admin_user_data_db.id,
        hash_password=admin_user_data_db.hashPassword,
        key=b"key",
        salt=b"salt"
    )
    if not generator.check_password():
        return HTMLResponse(
            """
            <script>
            window.document.location.href = "./"
            </script>
            """
        )

    token = login_manager.create_access_token(
        data={
            "sub": data.username
        }
    )

    response = HTMLResponse(
        """
        <script>
        window.document.location.href = "../"
        </script>
        """
    )
    login_manager.set_cookie(response, token)

    return response


@router.post("/login/logout")
def logout(request: Request):
    incorrect_token = "MoreliaTalk"

    response = HTMLResponse(
        """
        <script>
        window.document.location.href = "../"
        </script>
        """
    )

    login_manager.set_cookie(response, incorrect_token)

    return response
