import unittest
from packages.datamodel.tag import Tag

__author__ = 'anaeanet'


class TagTest(unittest.TestCase):

    def setUp(self):
        self.tag_id = 1
        self.tag_name = "tag1"
        self.tag = Tag(self.tag_id, self.tag_name)

    def test_constructor(self):
        self.assertEqual(self.tag.id, self.tag_id)
        self.assertEqual(self.tag.name, self.tag_name)

    def test_modification(self):
        with self.assertRaises(AttributeError): self.tag.id = None
        with self.assertRaises(AttributeError): self.tag.name = None


if __name__ == '__main__':
    unittest.main()
