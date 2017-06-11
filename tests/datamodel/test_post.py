import unittest
from packages.datamodel.post import Post
from packages.datamodel.user import User
from packages.datamodel.poststate import PostState
from packages.datamodel.tag import Tag
from packages.datamodel.gallery import Gallery

__author__ = 'anaeanet'


class PostTest(unittest.TestCase):

    def setUp(self):
        self.post_id = 1
        self.post_user = User(1, name="user_name")
        self.post_title = "post_title"
        self.post_status = PostState.DRAFT
        self.post_content = "content"
        self.post_tags = [Tag(1,"tag1"), Tag(2, "tag2")]
        self.post_title_image = 1
        self.post_gallery = Gallery("gallery_title", [])
        self.post_tmsp_publish = "2000-01-01 10:00:00.00000"
        self.post_original_post = 1

        self.post = Post(self.post_id, self.post_user, self.post_title, self.post_status, content=self.post_content
                         , tags=self.post_tags, title_image=self.post_title_image, gallery=self.post_gallery
                         , tmsp_publish=self.post_tmsp_publish, original_post=self.post_original_post)

    def test_constructor(self):
        self.assertEqual(self.post.id, self.post_id)
        self.assertEqual(self.post.user, self.post_user)
        self.assertEqual(self.post.title, self.post_title)
        self.assertEqual(self.post.status, self.post_status)
        self.assertEqual(self.post.content, self.post_content)
        self.assertEqual(self.post.tags, self.post_tags)
        self.assertNotEqual(id(self.post.tags), id(self.post_tags))
        self.assertEqual(self.post.title_image, self.post_title_image)
        self.assertNotEqual(id(self.post.gallery), id(self.post_gallery))
        self.assertEqual(self.post.tmsp_publish, self.post_tmsp_publish)
        self.assertEqual(self.post.original_post, self.post_original_post)

    def test_modification(self):
        with self.assertRaises(AttributeError): self.post.id = None
        with self.assertRaises(AttributeError): self.post.user = None
        with self.assertRaises(AttributeError): self.post.title = None
        with self.assertRaises(AttributeError): self.post.status = None
        with self.assertRaises(AttributeError): self.post.content = None
        with self.assertRaises(AttributeError): self.post.tags = None
        with self.assertRaises(AttributeError): self.post.title_image = None
        with self.assertRaises(AttributeError): self.post.gallery = None
        with self.assertRaises(AttributeError): self.post.tmsp_publish = None
        with self.assertRaises(AttributeError): self.post.original_post = None


if __name__ == '__main__':
    unittest.main()
