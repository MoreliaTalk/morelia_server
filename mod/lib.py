import sys
from hashlib import blake2b
from hmac import compare_digest
from os import urandom

from mod import config


class Hash:
    """Сlass generates password hashes, hashes for sessions,
    authenticator ID's, checks passwords hashes.

    Args:
        password (str, required): password.

        uuid (int, required): unique user identity.

        salt (Any, required): Salt. additional unique identifier
             (there can be any line: mother's maiden name,
             favorite writer, etc.).

        key (Any, optional): Additional argument. Defaults to None.
            If the value of the 'key' parameter is 'None' then the function
            will generated it.

        hash_password (str, optional): password hash (previously calculated).

    """
    def __init__(self, password: str, uuid: int, salt: bytes = None,
                 key: bytes = None, hash_password: str = None):

        if salt is None:
            self.salt = urandom(16)
        else:
            self.salt = salt

        if key is None:
            self.key = urandom(20)
        else:
            self.key = key

        self.binary_password = password.encode('utf-8')
        self.uuid = uuid
        self.hash_password = hash_password
        self.size_password = config.PASSWORD_HASH_SIZE
        self.size_auth_id = config.AUTH_ID_HASH_SIZE

    def get_salt(self) -> bytes:
        return self.salt

    def get_key(self) -> bytes:
        return self.key

    def password_hash(self) -> str:
        """Function generates a password hash.

        Returns:
            str: Returns hash password.
        """
        hash_password = blake2b(self.binary_password,
                                digest_size=self.size_password,
                                key=self.key, salt=self.salt)
        return hash_password.hexdigest()

    def check_password(self) -> bool:
        """Function checks the password hash and original password.

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
        """Function generates an authenticator ID's for the client session
        connection to the server.

        Returns:
            str: Returns auth_id
        """
        uuid = self.uuid.to_bytes(self.uuid.bit_length(),
                                  byteorder=sys.byteorder)
        result = blake2b(uuid,
                         digest_size=self.size_auth_id,
                         salt=self.salt)
        return result.hexdigest()
