import unittest
import sys
import os

# Add path to directory with code being checked
# to variable 'PATH' to import modules from directory
# above the directory with the tests.
BASE_PATH = os.path.dirname(os.getcwd())
sys.path.append(os.path.split(BASE_PATH)[0])
from mod import api


class TestAPI(unittest.TestCase):
    pass


if __name__ == "__main__":
    unittest.main()
