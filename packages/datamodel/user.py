__author__ = 'anaeanet'


class User:

    def __init__(self, user_id, state):
        self.__user_id = user_id
        self.__state = state

    @property
    def id(self):
        return self.__user_id

    @property
    def state(self):
        return self.__state