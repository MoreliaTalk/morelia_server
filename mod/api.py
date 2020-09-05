import json
from typing import Any
from typing import Optional

from pydantic import BaseModel
from pydantic import EmailStr


class EditedMessage(BaseModel):
    class Config:
        title = 'Time of editing the message'
    time: Optional[int] = None
    status: Optional[bool] = None


class File(BaseModel):
    class Config:
        title = 'Files attached to the message'
    picture: Optional[bytes] = None
    video: Optional[bytes] = None
    audio: Optional[bytes] = None
    document: Optional[bytes] = None


class FromFlow(BaseModel):
    class Config:
        title = 'Information from chat id'
    id: Optional[int] = None


class Flow(BaseModel):
    class Config:
        title = 'List of chat rooms with their description and type'
    id: Optional[int] = None
    time: Optional[int] = None
    type: Optional[str] = None
    title: Optional[str] = None
    info: Optional[str] = None


class MessageFromUser(BaseModel):
    class Config:
        title = 'Information about forwarded message user'
    uuid: Optional[int] = None
    username: Optional[str] = None


class User(BaseModel):
    class Config:
        title = 'User information'
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
        title = 'Message options'
    id: Optional[int] = None
    text: Optional[str] = None
    from_user: Optional[MessageFromUser] = None
    time: Optional[int] = None
    from_flow: FromFlow = None
    file: Optional[File] = None
    emoji: Optional[bytes] = None
    edited: Optional[EditedMessage] = None
    reply_to: Optional[Any] = None


class Data(BaseModel):
    class Config:
        title = 'Main data-object'
    time: Optional[int] = None
    flow: Optional[Flow] = None
    message: Optional[Message] = None
    user: Optional[User] = None
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
    version: Optional[float] = None


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
                          sort_keys=False,
                          indent=4,
                          default=lambda o: o.__dict__)


if __name__ == "__main__":
    print('Shema=', ValidJSON.schema_json(indent=2))
