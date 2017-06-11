from packages.datamodel.abstractbotobject import AbstractBotObject

__author__ = 'anaeanet'


class User(AbstractBotObject):

    def __init__(self, user_id, state_class, name=None):
        self.__id = user_id
        self.__state_class = state_class
        self.__name = name

    @property
    def id(self):
        return self.__id

    @property
    def state_class(self):
        return self.__state_class

    @property
    def name(self):
        return self.__name
