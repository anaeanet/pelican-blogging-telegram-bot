import unittest
from packages.persistence.dbwrapper import DBWrapper

__author__ = 'anaeanet'


class DBWrapperTest(unittest.TestCase):

    def setUp(self):
        self.db_name = "test_db.sqlite"
        self.db = DBWrapper(self.db_name)
        self.db.setup()

    def test_user(self):
        # TODO
        self.assertTrue(False)

    def test_post(self):
        # TODO
        self.assertTrue(False)

    def test_tag(self):
        # TODO
        self.assertTrue(False)

    def test_post_tag(self):
        # TODO
        self.assertTrue(False)

    def test_image(self):
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
