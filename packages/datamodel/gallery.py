__author__ = 'anaeanet'


class Gallery:

    def __init__(self, title, images):
        self.__title = title
        self.__images = images

    @property
    def title(self):
        return self.__title

    @property
    def images(self):
        return self.__images
