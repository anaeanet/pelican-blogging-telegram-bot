from packages.bot.abstracttelegrambot import AbstractTelegramBot
from packages.persistence.pelicanmarkdowndatabasewrapper import PelicanMarkdownDatabaseWrapper
from packages.bot.state.idlestate import *

__author__ = "anaeanet"


class PelicanMarkdownBot(AbstractTelegramBot):
    """
    This bot is a concrete implementation of TelegramBot.
    It sets up its own start state and database 
    """

    def __init__(self, token):
        database = PelicanMarkdownDatabaseWrapper("database.sqlite")
        database.setup()
        super().__init__(token, database)

        #initialize statuses for all users on db
        for user in database.get_users():
            state_class = globals()[user[2]]
            user_state = state_class(self)
            super().set_user_state(user[0], user_state)
