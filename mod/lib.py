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

import sys
from hashlib import blake2b
from hmac import compare_digest
from os import urandom
import configparser

# ************** Read "config.ini" ********************
config = configparser.ConfigParser()
config.read('config.ini')
hash_size = config['HASH_SIZE']
# ************** END **********************************


class Hash:
    """Generates password hashes, hashes for sessions,
    authenticator ID's, checks passwords hashes.

    Args:
        password (str, required): password.

        uuid (int or str, [str convert to int], required): unique user
              identity.

        salt (Any, required): Salt. additional unique identifier
             (there can be any line: mother's maiden name,
             favorite writer, etc.).

        key (Any, optional): Additional argument. Defaults to None.
            If value of 'key' parameter is 'None' then function
            will generated it.

        hash_password (str, optional): password hash (previously calculated).

    """
    def __init__(self,
                 password: str,
                 uuid: int | str,
                 salt: bytes = None,
                 key: bytes = None,
                 hash_password: str = None):

        if salt is None:
            self.salt = urandom(16)
        else:
            self.salt = salt

        if key is None:
            self.key = urandom(20)
        else:
            self.key = key

        if isinstance(uuid, str):
            self.uuid = int(uuid)
        else:
            self.uuid = uuid

        self.binary_password = password.encode('utf-8')
        self.hash_password = hash_password
        self.size_password = hash_size.getint('password')
        self.size_auth_id = hash_size.getint('auth_id')

    @property
    def get_salt(self) -> bytes:
        return self.salt

    @property
    def get_key(self) -> bytes:
        return self.key

    def password_hash(self) -> str:
        """Generates a password hash.

        Returns:
            str: Returns hash password.
        """
        hash_password = blake2b(self.binary_password,
                                digest_size=self.size_password,
                                key=self.key,
                                salt=self.salt)
        return hash_password.hexdigest()

    def check_password(self) -> bool:
        """Checks password hash and original password.

        Returns:
            bool: True or False
        """
        if self.hash_password is None:
            return False
        else:
            verified_hash_password = self.password_hash()
            return compare_digest(self.hash_password,
                                  verified_hash_password)

    def auth_id(self) -> str:
        """Generates an authenticator ID's for client session
        connection to server.

        Returns:
            str: Returns auth_id
        """
        uuid = self.uuid.to_bytes(self.uuid.bit_length(),
                                  byteorder=sys.byteorder)
        result = blake2b(uuid,
                         digest_size=self.size_auth_id,
                         salt=self.salt)
        return result.hexdigest()
