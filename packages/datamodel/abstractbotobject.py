__author__ = 'anaeanet'


class AbstractBotObject:

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        if type(other) is type(self):
            return not self == other
        return NotImplemented

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))
