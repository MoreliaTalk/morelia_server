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

    time: Optional[int] = None
    type: Optional[str] = None  # noqa
    title: Optional[str] = None
    info: Optional[str] = None
    owner: Optional[str] = None
    users: Optional[List] = None
    message_start: Optional[int] = None
    message_end: Optional[int] = None


class BaseUser(BaseModel):
    """
    Base class describes validation of the User object.
    """

    uuid: Optional[str] = None
    login: Optional[str] = None
    username: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[bytes] = None
    password: Optional[str] = None
    is_bot: Optional[bool] = None
    auth_id: Optional[str] = None
    token_ttl: Optional[int] = None
    email: Optional[EmailStr] = None


class BaseMessage(BaseModel):
    """
    Base class describes validation Message object.
    """

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
    """
    Base class describes validation of the Data object.
    """

    time: Optional[int] = None
    user: Optional[List[BaseUser]] = None
    meta: Optional[Any] = None


class BaseErrors(BaseModel):
    """
    Base class describes validation of the Errors object.
    """

    detail: Optional[str] = None


class BaseVersion(BaseModel):
    """
    Base class describes validation of the Jsonapi object.
    """

    version: str
    revision: Optional[str] = None


class BaseValidator(BaseModel):
    """
    Base class describes validation of the Main object.
    """

    type: str  # noqa
    jsonapi: BaseVersion
    meta: Optional[Any] = None


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

    uuid: str = None


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

    flow: Optional[List[FlowRequest]] = None
    message: Optional[List[MessageRequest]] = None


class ErrorsRequest(BaseErrors):
    """
    Validation settings for the Errors object.
    """

    class Config:
        """
        Additional configuration for Request.
        """

        title = 'Error information'

    code: int = None
    status: str = None
    time: int = None


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

    data: Optional[DataRequest] = None
    errors: ErrorsRequest = None


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

    client_id: int = None


class DataResponse(BaseData):
    """
    Validation settings for the Data object.
    """

    class Config:
        """
        Additional configuration for Response.
        """

        title = 'Main data-object'

    flow: Optional[List[FlowResponse]] = None
    message: Optional[List[MessageResponse]] = None


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

    data: Optional[DataResponse] = None
    errors: ErrorsResponse = None
