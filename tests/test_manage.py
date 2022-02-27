import unittest

from click.testing import CliRunner

import manage


class CreateUser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner = CliRunner()

    def test_create_user(self):
        username = "UserHello"
        login = "login123"
        password = "password123"
        result = self.runner.invoke(manage.create_user, ["--username",
                                                         f"{username}",
                                                         "--login",
                                                         f"{login}",
                                                         "--password",
                                                         f"{password}"])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, f"{username} created, login: {login}, password: {password}\n")


class CreateFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner = CliRunner()

    def test_create_flow(self):
        result = self.runner.invoke(manage.create_flow)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, "Flow created")


if __name__ == "__main__":
    unittest.main()
