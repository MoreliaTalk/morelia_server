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

from uuid import uuid4
from fastapi import APIRouter
from fastapi import Form
from starlette.requests import Request
from starlette.responses import HTMLResponse

from mod.db import models

router = APIRouter()


@router.post("/manage/delete_user")
def delete_user(request: Request, uuid: str = Form(...)):
    dbquery = models.UserConfig.selectBy(uuid=uuid).getOne()

    fake_uuid = str(uuid4().int)

    dbquery.login = "User deleted"
    dbquery.password = fake_uuid
    dbquery.hashPassword = fake_uuid
    dbquery.username = "User deleted"
    dbquery.authId = fake_uuid
    dbquery.email = ""
    dbquery.avatar = b""
    dbquery.bio = "deleted"
    dbquery.salt = b"deleted"
    dbquery.key = b"deleted"

    response = HTMLResponse("""
        <script>
            window.document.location.href = "./"
        </script>
    """)
    return response
