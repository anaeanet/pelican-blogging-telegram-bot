import unittest
from packages.datamodel.tag import Tag

__author__ = 'anaeanet'


class TagTest(unittest.TestCase):

    def setUp(self):
        self.tag_id = 1
        self.tag_name = "tag1"
        self.tag1 = Tag(self.tag_id, self.tag_name)
        self.tag2 = Tag(self.tag_id, self.tag_name)

    def test_constructor(self):
        self.assertEqual(self.tag1.id, self.tag_id)
        self.assertEqual(self.tag1.name, self.tag_name)
        self.assertTrue(self.tag1, self.tag2)

        self.assertNotEqual(id(self.tag1), id(self.tag2))

    def test_modification(self):
        with self.assertRaises(AttributeError): self.tag1.id = None
        with self.assertRaises(AttributeError): self.tag1.name = None


if __name__ == '__main__':
    unittest.main()
