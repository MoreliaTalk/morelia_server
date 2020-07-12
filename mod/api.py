import json
from time import time
from typing import Any
from typing import Optional

from pydantic import BaseModel
from pydantic import ValidationError
from pydantic import EmailStr

API_VERSION: bool = 1.0


dict_json = {
    'type': 'user_info',
    'data': {
        'time': time(),
        'chat': {
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
            'from_chat': {
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
        'version': None
        },
    'meta': None
    }

encode_json = json.JSONEncoder().encode(dict_json)


class APIEditedMessage(BaseModel):
    class Config:
        title = 'Time of editing the message'
    time: int
    status: bool


class APIFile(BaseModel):
    class Config:
        title = 'Files attached to the message'
    picture: Optional[bytes] = None
    video: Optional[bytes] = None
    audio: Optional[bytes] = None
    document: Optional[bytes] = None


class APIFromChat(BaseModel):
    class Config:
        title = 'Information from chat id'
    id: int


class APIChat(BaseModel):
    class Config:
        title = 'List of chat rooms with their description and type'
    id: int
    time: Optional[int] = None
    type: Optional[str] = None
    title: Optional[str] = None
    info: Optional[str] = None


class APIMessageFromUser(BaseModel):
    class Config:
        title = 'Information about forwarded message user'
    id: int
    username: str


class APIUser(BaseModel):
    class Config:
        title = 'User information'
    id: int
    login: Optional[str] = None
    password: Optional[str] = None
    username: Optional[str] = None
    is_bot: Optional[bool] = None
    auth_id: int
    email: Optional[EmailStr] = None
    avatar: Optional[bytes] = None
    bio: Optional[str] = None


class APIMessage(BaseModel):
    class Config:
        title = 'Message options'
    id: int
    text: Optional[str] = None
    from_user: Optional[APIMessageFromUser] = None
    time: int
    from_chat: APIFromChat = None
    file: Optional[APIFile] = None
    emoji: Optional[bytes] = None
    edited: Optional[APIEditedMessage] = None
    reply_to: Optional[Any] = None


class APIData(BaseModel):
    class Config:
        title = 'Main data-object'
    time: Optional[int] = None
    chat: Optional[APIChat] = None
    message: Optional[APIMessage] = None
    user: Optional[APIUser] = None
    meta: Optional[Any] = None


class APIErrors(BaseModel):
    class Config:
        title = 'Error information and statuses of request processing'
    id: int
    time: int
    status: str
    code: int
    detail: str


class APIVersion(BaseModel):
    class Config:
        title = 'Protocol version'
    version: float


class JsonAPI(BaseModel):
    class Config:
        title = 'MoreliaTalk protocol v1.0'
    type: str
    data: Optional[APIData] = None
    errors: Optional[APIErrors] = None
    jsonapi: APIVersion
    meta: Optional[Any] = None


def response(obj):
    try:
        validate = JsonAPI.parse_raw(obj)
    except ValidationError as error:
        return error.json()
    if validate.dict()['type'] == 'all_messages':
        try:
            result = APIErrors(id=validate.dict()['data']['user']['id'], time=time(), status='OK', code=200, detail='Hello')
        except ValidationError as error:
            result = error
    elif validate.dict()['type'] == 'auth':
        try:
            result = APIErrors(id=validate.dict()['data']['user']['id'], time=time(), status='OK', code=200, detail='Hello')
        except ValidationError as error:
            result = error
    elif validate.dict()['type'] == 'all_chat':
        try:
            result = APIErrors(id=validate.dict()['data']['user']['id'], time=time(), status='OK', code=200, detail='Hello')
        except ValidationError as error:
            result = error
    elif validate.dict()['type'] == 'reg_user':
        try:
            result = APIErrors(id=validate.dict()['data']['user']['id'], time=time(), status='OK', code=200, detail='Hello')
        except ValidationError as error:
            result = error
    elif validate.dict()['type'] == 'user_info':
        try:
            result = APIErrors(id=validate.dict()['data']['user']['id'], time=time(), status='OK', code=200, detail='Hello')
        except ValidationError as error:
            result = error
    elif validate.dict()['type'] == 'send_message':
        try:
            result = APIErrors(id=validate.dict()['data']['user']['id'], time=time(), status='OK', code=200, detail='Hello')
        except ValidationError as error:
            result = error
    elif validate.dict()['type'] == 'get_update':
        try:
            result = APIErrors(id=validate.dict()['data']['user']['id'], time=time(), status='OK', code=200, detail='Hello')
        except ValidationError as error:
            result = error
    else:
        try:
            result = APIErrors(id=2, time=time(), status='ERROR', code=400, detail='Hello')
        except ValidationError as error:
            result = error
    return result.json()


print('Response=', response(encode_json))
print('Shema=', JsonAPI.schema_json(indent=2))
