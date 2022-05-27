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

from uuid import uuid4

from fastapi import APIRouter
from fastapi import Form
from starlette.requests import Request
from starlette.responses import HTMLResponse

from mod.config.config import ConfigHandler
from mod.db.dbhandler import DBHandler


config = ConfigHandler()
config_option = config.read()


router = APIRouter()

db_connect = DBHandler(config_option.uri)


@router.post("/manage/delete_user")
def delete_user(request: Request,
                uuid: str = Form(...)):
    """
    Delete admin user.
    After returns a response and redirecting to the main page of admin panel.

    Args:
        request: request for server
        uuid: uuid admin user

    Returns:
        response redirecting to the main admin page
    """

    fake_uuid = str(uuid4().int)

    db_connect.update_user(uuid=uuid,
                           login="User deleted",
                           password=fake_uuid,
                           hash_password=fake_uuid,
                           username="User deleted",
                           auth_id=fake_uuid,
                           email="",
                           avatar=b"",
                           bio="deleted",
                           key=b"deleted",
                           salt=b"deleted")

    response = HTMLResponse("""<script>
                            window.document.location.href = "./"
                            </script>""")
    return response
