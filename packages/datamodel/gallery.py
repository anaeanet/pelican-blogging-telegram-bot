__author__ = 'anaeanet'


class Gallery:

    def __init__(self, title, images):
        self.__title = title
        self.__images = [image for image in images]

    @property
    def title(self):
        return self.__title

    @property
    def images(self):
        return [image for image in self.__images]
