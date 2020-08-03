from hashlib import blake2b
from os import urandom
from hmac import compare_digest

from mod import config


class Hash:
    """A class that generates password hashes, hashes for sessions,
    checks passwords hashes.

    Args:
        password (str, required): password
        salt (str, required): Salt.
        key (str, optional): Additional argument. Defaults to None.
            If the value of the 'key' parameter is 'None' then the function
            will set it to 'byte-like object' equal to an empty string.
        hash_password (str, optional):
        uuid (int, optional):

    """
    def __init__(self, password: str,
                 salt: str,
                 hash_password: str = None,
                 key: str = None,
                 uuid: int = None):
        self.password = password.encode('utf-8')
        self.hash_password = hash_password
        self.salt = salt
        self.key = key
        self.uuid = uuid
        self.size_password = config.PASSWORD_HASH_SIZE
        self.size_auth_id = config.AUTH_ID_HASH_SIZE
        # TODO
        # add iterations for generating hash-functions

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
        hash_password = blake2b(self.password,
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
            salt = self.__gen_salt(self.salt)
            key = self.__gen_key(self.key)
            password = self.password_hash().encode('utf-8')
            result = blake2b(password,
                             digest_size=self.size_password,
                             key=key,
                             salt=salt)
            good_password = result.hexdigest()
            return compare_digest(self.hash_password,
                                  good_password.encode('utf-8'))

    def auth_id(self) -> str:
        """The function generates an authenticator for the client session
        connection to the server.

        Returns:
            str: Returns auth_id
        """
        if self.uuid is None:
            return None
        else:
            salt = self.salt.encode('utf-8')
            # TODO
            # Convert to bytes using the embedded 'to_bytes' function.
            # In future we will have to decide on the conversion settings.
            uuid = str(self.uuid).encode('utf-8')
            result = blake2b(uuid,
                             digest_size=self.size_auth_id,
                             salt=salt)
            return result.hexdigest()
