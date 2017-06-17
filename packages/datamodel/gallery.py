from packages.datamodel.abstractbotobject import AbstractBotObject
from packages.datamodel.image import Image

__author__ = 'anaeanet'


class Gallery(AbstractBotObject):

    def __init__(self, title, images):
        self.__title = title
        self.__images = [Image(image.id, image.name, image.file_id, image.file, thumb_id=image.thumb_id, caption=image.caption) for image in images]

    @property
    def title(self):
        return self.__title

    @property
    def images(self):
        return self.__images
