import sqlite3

__author__ = 'anaeanet'


class AbstractDatabaseWrapper:

    def __init__(self, database_name):
        self.database_name = database_name
        self.conn = sqlite3.connect(database_name)
        if type(self) is AbstractDatabaseWrapper:
            raise TypeError("Abstract class! Cannot be instantiated.")

    def setup(self):
        raise NotImplementedError("Abstract method! Implement in child class", type(self))