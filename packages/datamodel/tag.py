from packages.datamodel.abstractbotobject import AbstractBotObject

__author__ = 'anaeanet'

class Tag(AbstractBotObject):

    def __init__(self, tag_id, name):
        self.__id = tag_id
        self.__name = name

    @property
    def id(self):
        return self.__id

    @property
    def name(self):
        return self.__name