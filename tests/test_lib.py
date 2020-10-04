import os
import sys
import unittest

from loguru import logger

# Add path to directory with code being checked
# to variable 'PATH' to import modules from directory
# above the directory with the tests.
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.split(BASE_PATH)[0])
from mod import lib


class TestHash(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()

    def setUp(self):
        self.password = 'password'
        self.salt = 'salt'
        self.key = 'key',
        self.uuid = 1234
        self.generator = lib.Hash(self.password,
                                  self.uuid,
                                  self.salt,
                                  self.key)
        self.hash_password = self.generator.password_hash()

    def tearDown(self):
        del self.generator
        del self.hash_password
        del self.password
        del self.salt
        del self.key
        del self.uuid

    def test_check_str_in_result(self):
        self.assertIsInstance(self.generator.password_hash(),
                              str)

    def test_check_space_password(self):
        self.password = ' '
        self.generator = lib.Hash(self.password,
                                  self.uuid,
                                  self.salt)
        self.assertIsInstance(self.generator.password_hash(),
                              str)

    def test_check_256_symbols_password(self):
        self.password = 'HezyfR4BdO2CcGNsaaDsIYHVYFIJn9Fp \
                         ICpqnFoXBYXn71wnItwTT2lAzgI44ur7 \
                         sviD8RckgfSTfdI1pFjLDxiO0EuG8Twn \
                         B7ZS3svE4RKn2xDkB3eOQ611UxT6oLXx \
                         rtIcVa7VeMTZEVj7tT8miOLAmzg5pKYo \
                         kgUU2x14tLMnswSs8YA9Tfk44tvHufL8 \
                         BQkUrrleeRLmRJgX9YguuLZecQYwkuJL \
                         VPXzeNZwrEAUqMda3w4Dn3oRT4Ihuhpo'
        self.generator = lib.Hash(self.password,
                                  self.uuid,
                                  self.salt)
        self.assertIsInstance(self.generator.password_hash(),
                              str)

    def test_check_wrong_password_type(self):
        self.password = 123456789
        self.assertRaises(AttributeError,
                          lib.Hash,
                          self.password,
                          self.uuid,
                          self.salt)

    def test_wrong_hash_password_type(self):
        self.hash_password = 123456789
        generator = lib.Hash(self.password,
                             self.uuid,
                             self.salt,
                             hash_password=self.hash_password)
        self.assertRaises(TypeError,
                          generator.check_password)

    def test_check_wrong_uuid_type(self):
        self.uuid = '123123'
        generator = lib.Hash(self.password,
                             self.uuid,
                             self.salt)
        self.assertRaises(AttributeError,
                          generator.auth_id)

    def test_check_password(self):
        self.new_generator = lib.Hash(self.password,
                                      self.uuid,
                                      self.salt,
                                      self.key,
                                      hash_password=self.hash_password)
        self.assertTrue(self.new_generator.check_password())

    def test_check_auth_id(self):
        self.assertIsInstance(self.generator.auth_id(),
                              str)


if __name__ == "__main__":
    unittest.main()
