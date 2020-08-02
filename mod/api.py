from typing import Any
from typing import Optional

from pydantic import BaseModel
from pydantic import EmailStr


""" Full JSON-object
dict_json = {
    'type': 'user_info',
    'data': {
        'time': time(),
        'flow': {
            'id': 1254,
            'time': time(),
            'type': 'chat',
            'title': 'Name Chat',
            'info': 'Info about this chat'
            },
        'message': {
            'id': 1,
            'text': 'some text...',
            'from_user': {
                'id': 1254,
                'username': 'Vasya'
                },
            'time': time(),
            'from_flow': {
                'id': 123655455
                },
            'file': {
                'picture': 'jkfikdkdsd',
                'video': 'sdfsdfsdf',
                'audio': 'fgfsdfsdfsdf',
                'document': ''
                },
            'emoji': 'sfdfsdfsdf',
            'edited': {
                'time': time(),
                'status': True
                },
            'reply_to': None
            },
        'user': {
            'id': 5855,
            'login': 'username1',
            'password': 'lksdjflksjfsd',
            'username': 'Vasya',
            'is_bot': True,
            'auth_id': '464645646464',
            'email': 'stepan.skrjabin@gmail.com',
            'avatar': 'fffdddddd',
            'bio': 'My bio'
            },
        'meta': None
        },
    'errors': {
        'id': 25665546,
        'time': time(),
        'status': 'OK',
        'code': 200,
        'detail': 'successfully'
        },
    'jsonapi': {
        'version': config.API_VERSION
        },
    'meta': None
    }
"""


class EditedMessage(BaseModel):
    class Config:
        title = 'Time of editing the message'
    time: int
    status: bool


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
    id: int


class Flow(BaseModel):
    class Config:
        title = 'List of chat rooms with their description and type'
    id: int
    time: Optional[int] = None
    type: Optional[str] = None
    title: Optional[str] = None
    info: Optional[str] = None


class MessageFromUser(BaseModel):
    class Config:
        title = 'Information about forwarded message user'
    id: int
    username: str


class User(BaseModel):
    class Config:
        title = 'User information'
    uuid: int = None
    login: Optional[str] = None
    password: Optional[str] = None
    username: Optional[str] = None
    is_bot: Optional[bool] = None
    auth_id: int = None
    email: Optional[EmailStr] = None
    avatar: Optional[bytes] = None
    bio: Optional[str] = None


class Message(BaseModel):
    class Config:
        title = 'Message options'
    id: int
    text: Optional[str] = None
    from_user: Optional[MessageFromUser] = None
    time: int
    from_flow: FromFlow = None
    file: Optional[File] = None
    emoji: Optional[bytes] = None
    edited: Optional[EditedMessage] = None
    reply_to: Optional[Any] = None


class Data(BaseModel):
    class Config:
        title = 'Main data-object'
    time: Optional[int] = None
    chat: Optional[Flow] = None
    message: Optional[Message] = None
    user: Optional[User] = None
    meta: Optional[Any] = None


class Errors(BaseModel):
    class Config:
        title = 'Error information and statuses of request processing'
    id: int
    time: int
    status: str
    code: int
    detail: str


class Version(BaseModel):
    class Config:
        title = 'Protocol version'
    version: float


class ValidJSON(BaseModel):
    class Config:
        title = 'MoreliaTalk protocol v1.0'
    type: str
    data: Optional[Data] = None
    errors: Optional[Errors] = None
    jsonapi: Version
    meta: Optional[Any] = None


if __name__ == "__main__":
    print('Shema=', ValidJSON.schema_json(indent=2))
