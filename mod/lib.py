from time import time
import sys
import json
from typing import Optional
from typing import Union
from hashlib import blake2b
from os import urandom
from hmac import compare_digest

from loguru import logger

from mod import config
from mod import api


class Hash:
    """Сlass generates password hashes, hashes for sessions,
    checks passwords hashes.

    Args:
        password (str, required): password.

        salt (str, required): Salt. additional unique identifier
             (there can be any line: mother's maiden name,
             favorite writer, etc.).

        key (str, optional): Additional argument. Defaults to None.
            If the value of the 'key' parameter is 'None' then the function
            will set it to 'byte-like object' equal to an empty string.

        hash_password (str, optional): password hash (previously calculated).

        uuid (int, optional): unique user identity.

    """
    def __init__(self, password: str,
                 salt: str,
                 hash_password: str = None,
                 key: str = None,
                 uuid: int = None):
        self.binary_password = password.encode('utf-8')
        self.hash_password = hash_password
        self.salt = salt
        self.key = key
        self.uuid = uuid
        self.size_password = config.PASSWORD_HASH_SIZE
        self.size_auth_id = config.AUTH_ID_HASH_SIZE

    def __gen_salt(self, _salt: str) -> bytes:
        if _salt is None:
            _salt = urandom(16)
            return _salt
        else:
            return _salt.encode('utf-8')

    def __gen_key(self, _key: str) -> bytes:
        if _key is not None:
            return _key.encode('utf-8')
        else:
            _key = b''
            return _key

    def password_hash(self) -> str:
        """Function generates a password hash.

        Returns:
            str: Returns hash password.
        """
        salt = self.__gen_salt(self.salt)
        key = self.__gen_key(self.key)
        hash_password = blake2b(self.binary_password,
                                digest_size=self.size_password,
                                key=key, salt=salt)
        return hash_password.hexdigest()

    def check_password(self) -> bool:
        """The function checks the password hash and original password.

        Returns:
            bool: True or False
        """
        if self.hash_password is None:
            return False
        else:
            verified_hash_password = self.password_hash()
            return compare_digest(self.hash_password,
                                  verified_hash_password)

    def auth_id(self) -> Optional[str]:
        """The function generates an authenticator for the client session
        connection to the server.

        Returns:
            str: Returns auth_id
        """
        if self.uuid is None:
            return None
        else:
            salt = self.salt.encode('utf-8')
            uuid = self.uuid.to_bytes(self.uuid.bit_length(),
                                      byteorder=sys.byteorder)
            result = blake2b(uuid,
                             digest_size=self.size_auth_id,
                             salt=salt)
            return result.hexdigest()


class ErrorsCatching():
    """Function catches errors in the "try...except" content.
    Result is 'dict' with information about the code, status,
    time and detailed description of the error that has occurred.
    For errors like Exception and other unrecognized errors,
    code "520" and status "Unknown Error" are used.
    Function also automatically logs the error.

    Args:
        code (Union[int, str]): Error code or type and exception description.
        add_info (Optional[str], optional): Additional information to be added.
                                            The 'Exception' field is not used
                                            for exceptions. Defaults to None.

    Returns:
        dict: returns 'dict' according to the protocol,
                like: {
                    'code': 200,
                    'status': 'Ok',
                    'time': 123456545,
                    'detail': 'successfully'
                    }


    """
    def __init__(self, code: Union[int, str],
                 add_info: Optional[str] = None):
        self.get_time = int(time.time())
        self.dict_all_errors = {
            200: {
                'status': 'OK',
                'detail': 'successfully'
                },
            201: {
                'status': 'Created',
                'detail': 'Created'
                },
            202: {
                'status': 'Accepted',
                'detail': 'Accepted'
                },
            400: {
                'status': 'Bad Request',
                'detail': 'Bad Request'
                },
            401: {
                'status': 'Unauthorized',
                'detail': 'Unauthorized'
                },
            403: {
                'status': 'Forbidden',
                'detail': 'Forbidden'
                },
            404: {
                'status': 'Not Found',
                'detail': 'Not Found'
                },
            405: {
                'status': 'Method Not Allowed',
                'detail': 'Method Not Allowed'
                },
            408: {
                'status': 'Request Timeout',
                'detail': 'Request Timeout'
                },
            409: {
                'status': 'Conflict',
                'detail': 'Such user (flow) is already on the server.'
                },
            415: {
                'status': 'Unsupported Media Type',
                'detail': 'Unsupported Media Type'
                },
            417: {
                'status': 'Expectation Failed',
                'detail': 'Expectation Failed'
                },
            426: {
                'status': 'Upgrade Required',
                'detail': 'Upgrade Required'
                },
            429: {
                'status': 'Too Many Requests',
                'detail': 'Too Many Requests'
                },
            499: {
                'status': 'Client Closed Request',
                'detail': 'Client Closed Request'
                },
            500: {
                'status': 'Internal Server Error',
                'detail': 'Internal Server Error'
                },
            503: {
                'status': 'Service Unavailable',
                'detail': 'Service Unavailable'
                },
            526: {
                'status': 'Invalid SSL Certificate',
                'detail': 'Invalid SSL Certificate'
                },
            }
        self.code = code
        self.add_info = add_info
        self.template = api.Errors()
        if self.code in self.dict_all_errors:
            if self.add_info is None:
                self.add_info = self.dict_all_errors[self.code]['detail']
            self.template.code = self.code
            self.template.status = self.dict_all_errors[self.code]['status']
            self.template.time = self.get_time
            self.template.detail = self.add_info
        else:
            self.template.code = 520
            self.template.status = 'Unknown Error'
            self.template.time = self.get_time
            self.template.detail = self.code

    def to_json(self):
        return json.dumps(self.template, indent=4,
                          default=lambda o: o.__dict__)

    def to_obj(self):
        return self.template

    def to_dict(self):
        return self.template.__dict__
