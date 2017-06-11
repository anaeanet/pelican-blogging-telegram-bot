import unittest
from packages.datamodel.gallery import Gallery

__author__ = 'anaeanet'


class GalleryTest(unittest.TestCase):

    def setUp(self):
        self.gallery_title = "Gallery-Title"
        self.gallery_images = []
        self.gallery1 = Gallery(self.gallery_title, self.gallery_images)
        self.gallery2 = Gallery(self.gallery_title, self.gallery_images)

    def test_constructor(self):
        self.assertEqual(self.gallery1.title, self.gallery_title)
        self.assertEqual(self.gallery1.images, self.gallery_images)
        self.assertEqual(self.gallery1, self.gallery2)

        self.assertNotEqual(id(self.gallery1.images), id(self.gallery_images))
        self.assertNotEqual(id(self.gallery1), id(self.gallery2))

    def test_modification(self):
        with self.assertRaises(AttributeError): self.gallery1.title = None
        with self.assertRaises(AttributeError): self.gallery1.images = []


if __name__ == '__main__':
    unittest.main()
