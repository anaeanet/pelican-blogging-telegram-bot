__author__ = 'anaeanet'


class Gallery:

    def __init__(self, name, images):
        self.__name = name
        self.__images = images

    @property
    def name(self):
        return self.__name

    @property
    def images(self):
        return self.__images
