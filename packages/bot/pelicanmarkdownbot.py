from packages.bot.abstracttelegrambot import AbstractTelegramBot
from packages.persistence.pelicanmarkdowndatabasewrapper import PelicanMarkdownDatabaseWrapper
from packages.bot.state.idlestate import IdleState

__author__ = "anaeanet"


class PelicanMarkdownBot(AbstractTelegramBot):
    """
    This bot is a concrete implementation of TelegramBot.
    It sets up its own start state and database 
    """

    def __init__(self):
        database = PelicanMarkdownDatabaseWrapper("database.sqlite")
        super().__init__(database)
        super().set_start_state(IdleState(self))
        database.setup()