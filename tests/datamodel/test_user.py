import unittest
from packages.datamodel.user import User

__author__ = 'anaeanet'


class UserTest(unittest.TestCase):

    def setUp(self):
        self.user_id = 1
        self.user_name = "user_name"
        self.user1 = User(self.user_id, name=self.user_name)
        self.user2 = User(self.user_id, name=self.user_name)

    def test_constructor(self):
        self.assertEqual(self.user1.id, self.user_id)
        self.assertEqual(self.user1.name, self.user_name)
        self.assertEqual(self.user1, self.user2)

        self.assertNotEqual(id(self.user1), id(self.user2))

    def test_modification(self):
        with self.assertRaises(AttributeError): self.user1.id = None
        with self.assertRaises(AttributeError): self.user1.name = None


if __name__ == '__main__':
    unittest.main()
