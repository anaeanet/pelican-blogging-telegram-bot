__author__ = 'anaeanet'


class User:

    def __init__(self, user_id, state=None, posts=[]):
        self.__id = user_id
        self.__state = state
        self.__posts = posts

    @property
    def id(self):
        return self.__id

    @property
    def state(self):
        return self.__state

    @property
    def posts(self):
        return self.__posts
