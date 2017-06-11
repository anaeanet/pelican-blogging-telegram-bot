import unittest
from packages.datamodel.user import User

__author__ = 'anaeanet'


class UserTest(unittest.TestCase):

    def setUp(self):
        self.user_id = 1
        self.user_name = "user_name"
        self.user = User(self.user_id, name=self.user_name)

    def test_constructor(self):
        self.assertEqual(self.user.id, self.user_id)
        self.assertEqual(self.user.name, self.user_name)

    def test_modification(self):
        with self.assertRaises(AttributeError): self.user.id = None
        with self.assertRaises(AttributeError): self.user.name = None


if __name__ == '__main__':
    unittest.main()
