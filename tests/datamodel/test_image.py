import unittest
from packages.datamodel.image import Image

__author__ = 'anaeanet'


class ImageTest(unittest.TestCase):

    def setUp(self):
        self.image_id = 1
        self.image_name = "IMG1.jpg"
        self.image_file_id = "file_id_1"
        self.image_file = "file_1"
        self.image_thumb_id = "thumb_id_1"
        self.image_caption = "caption_1"
        self.image1 = Image(self.image_id, self.image_name, self.image_file_id, self.image_file, thumb_id=self.image_thumb_id, caption=self.image_caption)
        self.image2 = Image(self.image_id, self.image_name, self.image_file_id, self.image_file, thumb_id=self.image_thumb_id, caption=self.image_caption)

    def test_constructor(self):
        self.assertEqual(self.image1.id, self.image_id)
        self.assertEqual(self.image1.name, self.image_name)
        self.assertEqual(self.image1.file_id, self.image_file_id)
        self.assertEqual(self.image1.file, self.image_file)
        self.assertEqual(self.image1.thumb_id, self.image_thumb_id)
        self.assertEqual(self.image1.caption, self.image_caption)
        self.assertEqual(self.image1, self.image2)

        self.assertNotEqual(id(self.image1), id(self.image2))

    def test_modification(self):
        with self.assertRaises(AttributeError): self.image1.id = None
        with self.assertRaises(AttributeError): self.image1.name = None
        with self.assertRaises(AttributeError): self.image1.file_id = None
        with self.assertRaises(AttributeError): self.image1.file = None
        with self.assertRaises(AttributeError): self.image1.thumb_id = None
        with self.assertRaises(AttributeError): self.image1.caption = None


if __name__ == '__main__':
    unittest.main()
