__author__ = "aneanet"


class AbstractState:

    def __init__(self):
        if type(self) is AbstractState:
            raise TypeError("Abstract class! Cannot be instantiated.")

    def process_update(self, update):
        raise NotImplementedError("Abstract method! Implement in child class", type(self))
