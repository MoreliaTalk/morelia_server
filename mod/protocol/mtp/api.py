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

from typing import Any
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import EmailStr

# Version of MoreliaTalk Protocol
VERSION = '1.0'
REVISION = '17'


# A description of the basic validation scheme for requests and responses.


class BaseFlow(BaseModel):
    """
    Base class describes validation of the Flow object.
    """

    time: Optional[int]
    type: Optional[str]  # noqa
    title: Optional[str]
    info: Optional[str]
    owner: Optional[str]
    users: Optional[List]
    message_start: Optional[int]
    message_end: Optional[int]


class BaseUser(BaseModel):
    """
    Base class describes validation of the User object.
    """

    uuid: Optional[str]
    login: Optional[str]
    username: Optional[str]
    bio: Optional[str]
    avatar: Optional[bytes]
    password: Optional[str]
    is_bot: Optional[bool]
    auth_id: Optional[str]
    token_ttl: Optional[int]
    email: Optional[EmailStr]


class BaseMessage(BaseModel):
    """
    Base class describes validation Message object.
    """

    uuid: str
    text: Optional[str]
    from_user: Optional[str]
    time: Optional[int]
    from_flow: Optional[str]
    file_picture: Optional[bytes]
    file_video: Optional[bytes]
    file_audio: Optional[bytes]
    file_document: Optional[bytes]
    emoji: Optional[bytes]
    edited_time: Optional[int]
    edited_status: Optional[bool]


class BaseData(BaseModel):
    """
    Base class describes validation of the Data object.
    """

    time: Optional[int]
    user: Optional[List[BaseUser]]
    meta: Optional[Any]


class BaseErrors(BaseModel):
    """
    Base class describes validation of the Errors object.
    """

    detail: Optional[str]


class BaseVersion(BaseModel):
    """
    Base class describes validation of the Jsonapi object.
    """

    version: str
    revision: Optional[str]


class BaseValidator(BaseModel):
    """
    Base class describes validation of the Main object.
    """

    type: str  # noqa
    jsonapi: BaseVersion
    meta: Optional[Any]


# Description of the request validation scheme


class FlowRequest(BaseFlow):
    """
    Validation settings for the Flow object.
    """

    class Config:
        """
        Additional configuration for Request.
        """

        title = 'List of flow with UUID is str or None'

    uuid: Optional[str]


class UserRequest(BaseUser):
    """
    Validation settings for the User object.
    """

    class Config:
        """
        Additional configuration for Request.
        """

        title = 'List of user information'


class MessageRequest(BaseMessage):
    """
    Validation settings for the Message object.
    """

    class Config:
        """
        Additional configuration for Request.
        """

        title = 'List of message information with client_id is int'

    client_id: int


class DataRequest(BaseData):
    """
    Validation settings for the Data object.
    """

    class Config:
        """
        Additional configuration for Request.
        """

        title = 'Main data-object'

    flow: Optional[List[FlowRequest]]
    message: Optional[List[MessageRequest]]


class ErrorsRequest(BaseErrors):
    """
    Validation settings for the Errors object.
    """

    class Config:
        """
        Additional configuration for Request.
        """

        title = 'Error information'

    code: Optional[int]
    status: Optional[str]
    time: Optional[int]


class VersionRequest(BaseVersion):
    """
    Validation settings for the Jsonapi object.
    """

    class Config:
        """
        Additional configuration for Request.
        """

        title = 'Protocol version'


class Request(BaseValidator):
    """
    Responsible for validation and generation of request in JSON-object.
    """

    class Config:
        """
        Additional configuration for Request.
        """

        title = 'MoreliaTalk protocol (for request)'

    data: Optional[DataRequest]
    errors: Optional[ErrorsRequest]


# Description of the response validation scheme


class FlowResponse(BaseFlow):
    """
    Validation settings for the Flow object.
    """

    class Config:
        """
        Additional configuration for Response.
        """

        title = 'List of flow with required UUID and it is str'

    uuid: str


class UserResponse(BaseUser):
    """
    Validation settings for the User object.
    """

    class Config:
        """
        Additional configuration for Response.
        """

        title = 'List of user information'


class MessageResponse(BaseMessage):
    """
    Validation settings for the Message object.
    """

    class Config:
        """
        Additional configuration for Response.
        """

        title = 'List of message information without client_id'

    client_id: Optional[int]


class DataResponse(BaseData):
    """
    Validation settings for the Data object.
    """

    class Config:
        """
        Additional configuration for Response.
        """

        title = 'Main data-object'

    flow: Optional[List[FlowResponse]]
    message: Optional[List[MessageResponse]]


class ErrorsResponse(BaseErrors):
    """
    Validation settings for the Errors object.
    """

    class Config:
        """
        Additional configuration for Response.
        """

        title = 'Error information. Code, status. time is required'

    code: int
    status: str
    time: int


class VersionResponse(BaseVersion):
    """
    Validation settings for the Jsonapi object.
    """

    class Config:
        """
        Additional configuration for Response.
        """

        title = 'Protocol version'


class Response(BaseValidator):
    """
    Responsible for validation and generation of response in JSON-object.
    """

    class Config:
        """
        Additional configuration for Response.
        """

        title = 'MoreliaTalk protocol (for response)'
        use_enum_values = False

    data: Optional[DataResponse]
    errors: Optional[ErrorsResponse]
