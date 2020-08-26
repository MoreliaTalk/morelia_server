import os
import sys
import unittest


# Add path to directory with code being checked
# to variable 'PATH' to import modules from directory
# above the directory with the tests.
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
FIXTURES_PATH = os.path.join(BASE_PATH, 'fixtures')
TEST_FILE = os.path.join(FIXTURES_PATH, 'api.json')
sys.path.append(os.path.split(BASE_PATH)[0])
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
