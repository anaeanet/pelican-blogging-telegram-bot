import unittest
from packages.datamodel.poststate import PostState

__author__ = 'anaeanet'


class UserTest(unittest.TestCase):

    def setUp(self):
        self.draft = PostState("draft")
        self.post = PostState("published")

    def test_constructor(self):
        self.assertEqual(self.draft, PostState.DRAFT)
        self.assertEqual(self.post, PostState.PUBLISHED)

    def test_modification(self):
        with self.assertRaises(AttributeError): self.draft.value = None
        with self.assertRaises(AttributeError): self.post.value = None


if __name__ == '__main__':
    unittest.main()
