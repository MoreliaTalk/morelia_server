import unittest
import sys
import os
from typing import Optional
from typing import Union


sys.path.append(os.path.dirname(os.getcwd()))
from mod import lib


class TestHash(unittest.TestCase):
    def setUp(self):
        self.password = 'password'
        self.salt = 'salt'
        self.key = 'key',
        self.uuid = 1234
        self.libhash = lib.Hash(self.password,
                                self.salt,
                                uuid=self.uuid)
        self.hash_password = self.libhash.password_hash()

    def tearDown(self):
        del self.libhash
        del self.hash_password

    def test_hash_password_hash_type_str(self):
        self.assertIsInstance(self.libhash.password_hash(),
                              str)

    def test_hash_check_password_type_bool(self):
        self.libhash = lib.Hash(self.password,
                                self.salt,
                                self.hash_password)
        self.assertTrue(self.libhash.check_password())

    def test_hash_auth_id_type_str(self):
        self.assertIsInstance(self.libhash.auth_id(),
                              str)


@unittest.skip
class TestErrorCatching(unittest.TestCase):
    def test_error_catching_type_dict(self):
        self.assertIsInstance(lib.error_catching('200'),
                              dict)

    def test_error_catching_start_range(self):
        self.assertEqual(lib.error_catching(200)['code'],
                         200)

    def test_error_catching_end_range(self):
        self.assertEqual(lib.error_catching(526)['code'],
                         526)

    def test_error_catching_detail_in_result(self):
        self.assertEqual(lib.error_catching('200')['detail'],
                         '200')

    def test_error_catching_code_in_result(self):
        self.assertEqual(lib.error_catching('200')['code'],
                         520)


if __name__ == "__main__":
    unittest.main()
