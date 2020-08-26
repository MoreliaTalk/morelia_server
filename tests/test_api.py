import unittest
import sys
import os
from pydantic import ValidationError

# Add path to directory with code being checked
# to variable 'PATH' to import modules from directory
# above the directory with the tests.
FIXTURES_PATH = '\\'.join((os.getcwd(), 'tests\\fixtures'))
TEST_FILE = '\\'.join((FIXTURES_PATH, 'api.json'))
BASE_PATH = os.path.dirname(os.getcwd())
sys.path.append(BASE_PATH)
from mod import api


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.test = api.ValidJSON.parse_file(TEST_FILE)

    def tearDown(self):
        self.test = {}

    def test_api(self):
        self.assertIsInstance(self.test.dict(), dict)


if __name__ == "__main__":
    unittest.main()
