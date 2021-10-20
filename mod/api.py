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

from typing import Any
from typing import Optional
from typing import List

from pydantic import BaseModel
from pydantic import EmailStr

# Version of MoreliaTalk Protocol
VERSION: str = '1.0'

# A description of the basic validation scheme for requests and responses.


class BaseFlow(BaseModel):
    time: Optional[int] = None
    type: Optional[str] = None
    title: Optional[str] = None
    info: Optional[str] = None
    owner: Optional[str] = None
    users: Optional[List] = None
    message_start: Optional[int] = None
    message_end: Optional[int] = None


class BaseUser(BaseModel):
    uuid: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[bytes] = None
    password: Optional[str] = None
    login: Optional[str] = None
    is_bot: Optional[bool] = None
    auth_id: Optional[str] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = None


class BaseMessage(BaseModel):
    uuid: str
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


class BaseData(BaseModel):
    time: Optional[int] = None
    user: Optional[List[BaseUser]] = None
    meta: Optional[Any] = None


class BaseErrors(BaseModel):
    detail: Optional[str] = None


class BaseVersion(BaseModel):
    version: str


class BaseValidator(BaseModel):
    type: str
    jsonapi: BaseVersion
    meta: Optional[Any] = None


# Description of the request validation scheme


class FlowRequest(BaseFlow):
    class Config:
        title = 'List of flow with UUID is str or None'
    uuid: str = None


class UserRequest(BaseUser):
    class Config:
        title = 'List of user information'
    pass


class MessageRequest(BaseMessage):
    class Config:
        title = 'List of message information with client_id is int'
    client_id: int


class DataRequest(BaseData):
    class Config:
        title = 'Main data-object'
    flow: Optional[List[FlowRequest]] = None
    message: Optional[List[MessageRequest]] = None


class ErrorsRequest(BaseErrors):
    class Config:
        title = 'Error information'
    code: int = None
    status: str = None
    time: int = None


class VersionRequest(BaseVersion):
    class Config:
        title = 'Protocol version'
    pass


class Request(BaseValidator):
    class Config:
        title = 'MoreliaTalk protocol (for request)'
    data: Optional[DataRequest] = None
    errors: ErrorsRequest = None


# Description of the response validation scheme


class FlowResponse(BaseFlow):
    class Config:
        title = 'List of flow with required UUID and it is str'
    uuid: str


class UserResponse(BaseUser):
    class Config:
        title = 'List of user information'
    pass


class MessageResponse(BaseMessage):
    class Config:
        title = 'List of message information without client_id'
    client_id: int = None


class DataResponse(BaseData):
    class Config:
        title = 'Main data-object'
    flow: Optional[List[FlowResponse]] = None
    message: Optional[List[MessageResponse]] = None


class ErrorsResponse(BaseErrors):
    class Config:
        title = 'Error information. Code, status. time is required'
    code: int
    status: str
    time: int


class VersionResponse(BaseVersion):
    class Config:
        title = 'Protocol version'
    pass


class Response(BaseValidator):
    class Config:
        title = 'MoreliaTalk protocol (for response)'
        use_enum_values = False
    data: Optional[DataResponse] = None
    errors: ErrorsResponse = None


if __name__ == "__main__":
    print('Shema for Response=', Response.schema_json(indent=2))
    print()
    print('Shema for Request=', Request.schema_json(indent=2))
