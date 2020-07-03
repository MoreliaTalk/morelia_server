import json
from time import time
from hashlib import blake2b
from os import urandom
from hmac import compare_digest
from typing import Any
from typing import Optional

from pydantic import BaseModel
from pydantic import ValidationError
from pydantic import EmailStr

API_VERSION: bool = 1.0


class PasswordValidate(BaseModel):
    password: bytes
    salt: bytes = None
    key: bytes = None
    hash_password: bytes = None


def password_hash(password: str, salt: bytes = None,
                  key: bytes = None) -> dict:
    """Function generates a a password hash.

    Args:
        password (str): password
        salt (bytes, optional): Salt. Defaults to None.
        key (bytes, optional): Additional argument. Defaults to None.
        If the value of the 'key' parameter is 'None' then the function
        will set it to 'byte-like object' equal to an empty string.

    Returns:
        dict: Returns the dictionary with the original parameters passed
        to the function and password hash.

    """
    valid = PasswordValidate(password=password, salt=salt, key=key)
    size: int = 32
    if valid.salt is None:
        salt = urandom(16)
    if valid.key is None:
        key = b''
    hash_password = blake2b(valid.password, digest_size=size, key=key, salt=salt)
    result = {
        'password': valid.password,
        'hash_password': hash_password.hexdigest().encode('utf-8'),
        'salt': valid.salt,
        'key': valid.key
    }
    return result


def check_password(hash_password: bytes, password: str,
                   salt: bytes, key: bytes = None) -> bool:
    """The function checks the password hash and original password.

    Args:
        hash_password (bytes): Hash password
        password (str): Password
        salt (bytes): Salt
        key (bytes, optional): Additional argument.
        If the hash password was obtained using an additional key "key",
        that key must be entered. Defaults to None.

    Returns:
        bool: True or False

    """
    data = password.encode('utf-8')
    size: int = 32
    if key is None:
        key = b''
    result = blake2b(data, digest_size=size, key=key, salt=salt)
    good_password = result.hexdigest()
    return compare_digest(hash_password, good_password.encode('utf-8'))


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

print('Size dict=', asizeof.asizeof(dict_json))
encode_json = json.JSONEncoder().encode(dict_json)
print('Size json=', asizeof.asizeof(encode_json))
print('Encode=', encode_json)


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
    if validate.dict()['type'] == 'user_info':
        try:
            result = APIErrors(id=1, time=time(), status='OK', code=200, detail='Hello')
        except ValidationError as error:
            result = error
    else:
        try:
            result = APIErrors(id=2, time=time(), status='ERROR', code=400, detail='Hello')
        except ValidationError as error:
            result = error
    return result.json()


print('Response=', response(encode_json))
#print('Shema=', JsonAPI.schema_json(indent=2))
