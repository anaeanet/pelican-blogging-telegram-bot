import unittest
from packages.datamodel.gallery import Gallery

__author__ = 'anaeanet'


class GalleryTest(unittest.TestCase):

    def setUp(self):
        self.gallery_title = "Gallery-Title"
        self.gallery_images = []
        self.gallery = Gallery(self.gallery_title, self.gallery_images)

    def test_constructor(self):
        self.assertEqual(self.gallery.title, self.gallery_title)
        self.assertEqual(self.gallery.images, self.gallery_images)
        self.assertNotEqual(id(self.gallery.images), id(self.gallery_images))

    def test_modification(self):
        with self.assertRaises(AttributeError): self.gallery.title = None
        with self.assertRaises(AttributeError): self.gallery.images = []


if __name__ == '__main__':
    unittest.main()
