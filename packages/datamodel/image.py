from packages.datamodel.abstractbotobject import AbstractBotObject

__author__ = 'anaeanet'


class Image(AbstractBotObject):

    def __init__(self, image_id, name, file_id, file, thumb_id=None, caption=None):
        self.__id = image_id
        self.__name = name
        self.__file_id = file_id
        self.__file = file
        self.__thumb_id = thumb_id
        self.__caption = caption

    @property
    def id(self):
        return self.__id

    @property
    def name(self):
        return self.__name

    @property
    def file_id(self):
        return self.__file_id

    @property
    def file(self):
        return self.__file

    @property
    def thumb_id(self):
        return self.__thumb_id

    @property
    def caption(self):
        return self.__caption
