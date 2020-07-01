import json
from time import time
from hashlib import blake2b
from os import urandom
from hmac import compare_digest


API_VERSION: bool = 1.0


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
    data = password.encode('utf-8')
    size: int = 32
    if salt is None:
        salt = urandom(16)
    if key is None:
        key = b''
    hash_password = blake2b(data, digest_size=size, key=key, salt=salt)
    result = {
        'password': password,
        'hash_password': hash_password.hexdigest().encode('utf-8'),
        'salt': salt,
        'key': key
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


async def response(request: dict) -> bytes:
    if request['type'] == 'get_update':
        result = {
            'type': request['type'],
            'data': {
                'time': request['data']['time'],
                'chat': {
                    'id': request['data']['chat']['id'],
                    'time': request['data']['time'],
                    'type': 'chat',
                    'title': 'Name Chat',
                    'info': 'Info about this chat'
                },
                'message': {
                    'id': 1,
                    'text': 'some text...',
                    'from_user': {'user': 'User'},
                    'time': request['data']['time'],
                    'file': {
                        'picture': None,
                        'video': None,
                        'audio': None,
                        'document': None
                    },
                    'emoji': None,
                    'edited': {
                        'time': None,
                        'status': False
                    },
                    'reply_to': None
                },
                'user': 'User',
                'meta': None
            },
            'errors': {
                'id': '',
                'time': time(),
                'status': 'OK',
                'code': 200,
                'detail': 'successfully'
            },
            'jsonapi': API_VERSION,
            'meta': None
        }
    result_bytes = json.JSONEncoder().encode(result)
    return result_bytes.encode()
