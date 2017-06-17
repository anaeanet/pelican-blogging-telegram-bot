__author__ = "aneanet"


class AbstractState:
    """
    Abstract state class.
    It provides access to its context and a single method to be implemented by all child classes.
    """

    def __init__(self, bot):
        self.__bot = bot
        if type(self) is AbstractState:
            raise TypeError("Abstract class! Cannot be instantiated.")

    @property
    def bot(self):
        return self.__bot

    def process_update(self, update):
        raise NotImplementedError("Abstract method! Implement in child class", type(self))
