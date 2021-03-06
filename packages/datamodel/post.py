from packages.datamodel.abstractbotobject import AbstractBotObject
from packages.datamodel.poststate import PostState
from packages.datamodel.tag import Tag
from packages.datamodel.gallery import Gallery


__author__ = 'anaeanet'


class Post(AbstractBotObject):

    def __init__(self, post_id, user, title, status, content="", tags=[], title_image=None, gallery=None, tmsp_publish=None, original_post=None):
        self.__id = post_id
        self.__user = user
        self.__title = title
        self.__status = PostState(status.value)
        self.__content = content
        self.__tags = [Tag(tag.id, tag.name) for tag in tags]
        self.__title_image = title_image
        self.__gallery = Gallery(gallery.title, gallery.images) if gallery is not None else None
        self.__tmsp_publish = tmsp_publish
        self.__original_post = original_post

    @property
    def id(self):
        return self.__id

    @property
    def user(self):
        return self.__user

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
    def tmsp_publish(self):
        return self.__tmsp_publish

    @property
    def original_post(self):
        return self.__original_post
