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

import json
from typing import Any
from typing import Optional
from typing import List

from pydantic import BaseModel
from pydantic import EmailStr

# Version of MoreliaTalk Protocol
VERSION: str = '1.0'


class Flow(BaseModel):
    class Config:
        title = 'List of flow with description and type'
    uuid: Optional[str] = None
    time: Optional[int] = None
    type: Optional[str] = None
    title: Optional[str] = None
    info: Optional[str] = None
    owner: Optional[str] = None
    users: Optional[List] = None
    message_start: Optional[int] = None
    message_end: Optional[int] = None


class User(BaseModel):
    class Config:
        title = 'List of user information'
    uuid: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[bytes] = None
    password: Optional[str] = None
    login: Optional[str] = None
    is_bot: Optional[bool] = None
    auth_id: Optional[str] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = None


class Message(BaseModel):
    class Config:
        title = 'List of message information'
    uuid: Optional[str] = None
    client_id: Optional[int] = None
    text: Optional[str] = None
    from_user: Optional[str] = None
    time: Optional[int] = None
    from_flow: Optional[str] = None
    file_picture: Optional[bytes] = None
    file_video: Optional[bytes] = None
    file_audio: Optional[bytes] = None
    file_document: Optional[bytes] = None
    emoji: Optional[bytes] = None
    edited_time: Optional[int] = None
    edited_status: Optional[bool] = None


class Data(BaseModel):
    class Config:
        title = 'Main data-object'
    time: Optional[int] = None
    flow: Optional[List[Flow]] = None
    message: Optional[List[Message]] = None
    user: Optional[List[User]] = None
    meta: Optional[Any] = None


class Errors(BaseModel):
    class Config:
        title = 'Error information and statuses of request processing'
    code: Optional[int] = None
    status: Optional[str] = None
    time: Optional[int] = None
    detail: Optional[str] = None


class Version(BaseModel):
    class Config:
        title = 'Protocol version'
    version: Optional[str] = None


class ValidJSON(BaseModel):
    class Config:
        title = 'MoreliaTalk protocol v1.0'
    type: Optional[str] = None
    data: Optional[Data] = None
    errors: Optional[Errors] = None
    jsonapi: Optional[Version] = None
    meta: Optional[Any] = None

    def toJSON(self):
        return json.dumps(self,
                          ensure_ascii=False,
                          default=lambda o: o.__dict__)


if __name__ == "__main__":
    print('Shema=', ValidJSON.schema_json(indent=2))
