import unittest
import sys
import os
from loguru import logger

# Add path to directory with code being checked
# to variable 'PATH' to import modules from directory
# above the directory with the tests.
BASE_PATH = os.path.dirname(os.getcwd())
sys.path.append(BASE_PATH)
from mod import lib


class TestHash(unittest.TestCase):
    """Modular tests for Hash class.
    It checks if function is working with correct data and
    also checks if there are any excitations when transmitting
    incorrect parameters.

    """
    # Basic settings for each test
    def setUp(self):
        self.password = 'password'
        self.salt = 'salt'
        self.key = 'key',
        self.uuid = 1234
        self.libhash = lib.Hash(self.password,
                                self.salt,
                                uuid=self.uuid)
        self.hash_password = self.libhash.password_hash()

    # Cleaning of objects created in settings function
    # is applied after each test.
    def tearDown(self):
        del self.libhash
        del self.hash_password

    def test_hash_password_hash_check_result_type(self):
        self.assertIsInstance(self.libhash.password_hash(),
                              str)

    def test_hash_password_hash_check_space_password(self):
        self.password = ' '
        self.libhash = lib.Hash(self.password,
                                self.salt)
        self.assertIsInstance(self.libhash.password_hash(),
                              str)

    def test_hash_password_hash_check_256_symbols_password(self):
        self.password = 'HezyfR4BdO2CcGNsaaDsIYHVYFIJn9Fp \
                         ICpqnFoXBYXn71wnItwTT2lAzgI44ur7 \
                         sviD8RckgfSTfdI1pFjLDxiO0EuG8Twn \
                         B7ZS3svE4RKn2xDkB3eOQ611UxT6oLXx \
                         rtIcVa7VeMTZEVj7tT8miOLAmzg5pKYo \
                         kgUU2x14tLMnswSs8YA9Tfk44tvHufL8 \
                         BQkUrrleeRLmRJgX9YguuLZecQYwkuJL \
                         VPXzeNZwrEAUqMda3w4Dn3oRT4Ihuhpo'
        self.libhash = lib.Hash(self.password,
                                self.salt)
        self.assertIsInstance(self.libhash.password_hash(),
                              str)

    def test_hash_password_hash_check_wrong_password_type(self):
        self.password = 123456789
        self.assertRaises(AttributeError,
                          lib.Hash,
                          self.password,
                          self.salt)

    def test_hash_password_hash_check_wrong_salt_type(self):
        self.salt = 123456789
        libhash = lib.Hash(self.password,
                           self.salt)
        self.assertRaises(AttributeError,
                          libhash.password_hash)

    def test_hash_password_hash_check_wrong_hash_password_type(self):
        self.hash_password = 123456789
        libhash = lib.Hash(self.password,
                           self.salt,
                           hash_password=self.hash_password)
        self.assertRaises(TypeError,
                          libhash.check_password)

    def test_hash_password_hash_check_key_type(self):
        self.key = 123456789
        libhash = lib.Hash(self.password,
                           self.salt,
                           key=self.key)
        self.assertRaises(AttributeError,
                          libhash.password_hash)

    def test_hash_password_hash_chech_wrong_uuid_type(self):
        self.uuid = '123123'
        libhash = lib.Hash(self.password,
                           self.salt,
                           uuid=self.uuid)
        self.assertRaises(AttributeError,
                          libhash.auth_id)

    def test_hash_check_password_check_result_type(self):
        self.libhash = lib.Hash(self.password,
                                self.salt,
                                self.hash_password)
        self.assertTrue(self.libhash.check_password())

    def test_hash_auth_id_check_result_type(self):
        self.assertIsInstance(self.libhash.auth_id(),
                              str)


class TestErrorCatching(unittest.TestCase):
    """Modular tests for 'error_catching' function.
    It checks if the function is working with correct data
    and also checks if incorrect parameters are being processed.

    """

    def setUp(self):
        logger.remove()

    def test_error_catching_check_result_type(self):
        self.assertIsInstance(lib.error_catching('200'),
                              dict)

    def test_error_catching_check_start_range(self):
        self.assertEqual(lib.error_catching(200)['code'],
                         200)

    def test_error_catching_check_end_range(self):
        self.assertEqual(lib.error_catching(526)['code'],
                         526)

    def test_error_catching_check_add_info_in_result(self):
        self.assertEqual(lib.error_catching('200')['detail'],
                         '200')

    def test_error_catching_code_in_result(self):
        self.assertEqual(lib.error_catching('200')['code'],
                         520)


if __name__ == "__main__":
    unittest.main()
