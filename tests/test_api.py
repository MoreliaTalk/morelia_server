import os
import sys
import unittest
from loguru import logger

# Add path to directory with code being checked
# to variable 'PATH' to import modules from directory
# above the directory with the tests.
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
FIXTURES_PATH = os.path.join(BASE_PATH, 'fixtures')
VALID_JSON = os.path.join(FIXTURES_PATH, 'api.json')
sys.path.append(os.path.split(BASE_PATH)[0])
from mod import api


class TestAPI(unittest.TestCase):
    def setUpClass(cls):
        logger.remove()

    def setUp(self):
        self.valid = api.ValidJSON.parse_file(VALID_JSON)

    def tearDown(self):
        del self.valid

    def test_validation_json(self):
        self.assertIsInstance(self.test.dict(), dict)


if __name__ == "__main__":
    unittest.main()
