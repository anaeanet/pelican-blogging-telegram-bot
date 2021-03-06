import unittest
import sqlite3
from packages.persistence.dbwrapper import DBWrapper
from packages.states.navigation.idlestate import IdleState

__author__ = 'anaeanet'


class TestDBWrapper(DBWrapper):

    def __init__(self, db_name):
        super().__init__()
        self.__conn = sqlite3.connect(db_name)


class DBWrapperTest(unittest.TestCase):

    def setUp(self):
        self.db_name = "database_test.sqlite"
        self.db = TestDBWrapper(self.db_name)
        self.db.setup()

    def test_user(self):
        user_id = 1
        user_state = IdleState(None, user_id)
        user_name = "user1"
        user = self.db.add_user(user_id, user_state, name=user_name)
        users = self.db.get_users()
        updated_user = self.db.update_user(user_id, user_state, name="updated_user")

        self.assertTrue(len(users) == 1)
        self.assertTrue(user in users)
        self.assertTrue(self.db.get_user(user_id) == updated_user)
        self.assertEqual(self.db.delete_user(user_id), updated_user)

    def test_tag(self):
        tag_name = "tag1"
        tag = self.db.add_tag(tag_name)
        tags = self.db.get_tags()

        self.assertTrue(len(tags) == 1)
        self.assertTrue(tag in tags)
        self.assertEqual(self.db.delete_tag(tag.id), tag)

    def test_image(self):
        file_id = "file_id"
        file_name = "file_name"
        file = "abcdefgh"
        thumb_id = "hgfedcba"
        image = self.db.add_image(file_id, file_name, file, thumb_id=thumb_id)
        images = self.db.get_images()

        self.assertTrue(len(images) == 1)
        self.assertTrue(image in images)
        self.assertEqual(self.db.delete_image(image.id), image)

    def test_post(self):
        # TODO
        self.assertTrue(False)

    def test_post_tag(self):
        # TODO
        self.assertTrue(False)

    def test_post_image(self):
        # TODO
        self.assertTrue(False)

    def tearDown(self):
        import subprocess
        subprocess.call(["rm", self.db_name])

if __name__ == '__main__':
    unittest.main()
