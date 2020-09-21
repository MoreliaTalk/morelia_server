import json
from typing import Any
from typing import Optional
# from typing import Union
from typing import List

from pydantic import BaseModel
from pydantic import EmailStr


class Flow(BaseModel):
    class Config:
        title = 'List of flow with description and type'
    id: Optional[int] = None
    time: Optional[int] = None
    type: Optional[str] = None
    title: Optional[str] = None
    info: Optional[str] = None


class User(BaseModel):
    class Config:
        title = 'List of user information'
    uuid: Optional[int] = None
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
    id: Optional[int] = None
    text: Optional[str] = None
    from_user_uuid: Optional[int] = None
    time: Optional[int] = None
    from_flow_id: Optional[int] = None
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

    def toJSON(self, sort_keys=False, indent=4):
        return json.dumps(self,
                          sort_keys=sort_keys,
                          indent=indent,
                          default=lambda o: o.__dict__)


if __name__ == "__main__":
    print('Shema=', ValidJSON.schema_json(indent=2))
