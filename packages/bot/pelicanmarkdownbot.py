import importlib

from packages.bot.abstracttelegrambot import AbstractTelegramBot
from packages.persistence.sqldbwrapper import SQLDBWrapper
from packages.bot.state.idlestate import *

__author__ = "anaeanet"


class PelicanMarkdownBot(AbstractTelegramBot):
    """
    This bot is a concrete implementation of TelegramBot.
    It sets up its own start state and database 
    """

    def __init__(self, token_url, start_state_class, authorized_users):
        super().__init__(token_url)
        self.__start_state_class = ".".join([start_state_class.__module__, start_state_class.__name__])
        self.__user_state = dict()
        self.__database = SQLDBWrapper("database.sqlite")
        self.__database.setup()

        # store all authorized users on database
        for user_id in authorized_users:
            if not self.__database.get_users(user_id=user_id):
                self.__database.add_user(user_id, True, self.__start_state_class)
            else:
                self.__database.update_user(user_id, is_authorized=True)

        #initialize statuses for all users on db
        for user in self.__database.get_users(is_authorized=True):
            # TODO move array access somewhere else
            self.__user_state[user[0]] = self.__deserialize_class(user[2])

    def __deserialize_class(self, module_dot_class):
        split_pos = module_dot_class.rfind(".")
        return getattr(importlib.import_module(module_dot_class[:split_pos]), module_dot_class[split_pos+1:])(self)

    def handle_update(self, update):
        user_id = None

        for key in update:
            if key == "update_id":
                continue
            else:
                user_id = update[key]["from"]["id"]
                if user_id not in self.__user_state or self.__user_state[user_id] is None:
                    self.__user_state[user_id] = self.__deserialize_class(self.__start_state_class)

        self.__user_state[user_id].process_update(update)