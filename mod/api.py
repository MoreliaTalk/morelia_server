import json
from typing import Any
from typing import Optional
from typing import Union
from typing import List

from pydantic import BaseModel
from pydantic import EmailStr


class EditedMessage(BaseModel):
    class Config:
        title = 'Status and time of editing message'
    time: Optional[int] = None
    status: Optional[bool] = None


class File(BaseModel):
    class Config:
        title = 'Files attached to message'
    picture: Optional[bytes] = None
    video: Optional[bytes] = None
    audio: Optional[bytes] = None
    document: Optional[bytes] = None


class FromFlow(BaseModel):
    class Config:
        title = 'Id flow attached for message'
    id: Optional[int] = None


class Flow(BaseModel):
    class Config:
        title = 'List of flow with description and type'
    id: Optional[int] = None
    time: Optional[int] = None
    type: Optional[str] = None
    title: Optional[str] = None
    info: Optional[str] = None


class MessageFromUser(BaseModel):
    class Config:
        title = 'UUID user who write this message'
    uuid: Optional[int] = None


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
    from_user: Optional[MessageFromUser] = None
    time: Optional[int] = None
    from_flow: Optional[FromFlow] = None
    file: Optional[File] = None
    emoji: Optional[bytes] = None
    edited: Optional[EditedMessage] = None


class Data(BaseModel):
    class Config:
        title = 'Main data-object'
    time: Optional[int] = None
    flow: Union[List[Flow], Flow] = None
    message: Union[List[Message], Message] = None
    user: Union[List[User], User] = None
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
