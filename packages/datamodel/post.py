__author__ = 'anaeanet'


class Post:

    def __init__(self, post_id, title, status, content=None, tags=[], title_image=None, gallery=None, original_post=None, tmsp_publish=None):
        self.__id = post_id
        self.__title = title
        self.__status = status
        self.__content = content
        self.__tags = tags
        self.__title_image = title_image
        self.__gallery = gallery
        self.__original_post = original_post
        self.__tmsp_publish = tmsp_publish

    @property
    def id(self):
        return self.__id

    @property
    def title(self):
        return self.__title

    @property
    def status(self):
        return self.__status

    @property
    def content(self):
        return self.__content

    @property
    def tags(self):
        return self.__tags

    @property
    def title_image(self):
        return self.__title_image

    @property
    def gallery(self):
        return self.__gallery

    @property
    def original_post(self):
        return self.__original_post

    @property
    def tmsp_publish(self):
        return self.__tmsp_publish
