from packages.datamodel.abstractbotobject import AbstractBotObject
from enum import Enum

__author__ = 'anaeanet'


class PostState(AbstractBotObject, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
