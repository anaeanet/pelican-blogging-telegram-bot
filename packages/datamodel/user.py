__author__ = 'anaeanet'


class User:

    # TODO possibly add user name

    def __init__(self, user_id):
        self.__id = user_id

    @property
    def id(self):
        return self.__id
