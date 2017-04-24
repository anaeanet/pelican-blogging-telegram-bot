__author__ = "aneanet"


class AbstractState:

    def __init__(self, context):
        self.__context = context
        if type(self) is AbstractState:
            raise TypeError("Abstract class! Cannot be instantiated.")

    def get_context(self):
        return self.__context

    def process_update(self, update):
        raise NotImplementedError("Abstract method! Implement in child class", type(self))
