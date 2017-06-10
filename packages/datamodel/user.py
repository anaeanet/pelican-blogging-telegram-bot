__author__ = 'anaeanet'


class User:

    # TODO possibly add user name

    def __init__(self, user_id, name=None):
        self.__id = user_id
        self.__name = name

    @property
    def id(self):
        return self.__id

    @property
    def name(self):
        return self.__name