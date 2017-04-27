from packages.bot.abstractuserstatebot import AbstractUserStateBot
import packages.bot.telegram as telegram

__author__ = "anaeanet"


class PelicanMarkdownBot(AbstractUserStateBot):
    """
    This bot is a concrete implementation of a telegram bot.
    It adds a persistence layer and only responds to authorized users.
    
    Its purpose is to create and maintain <a href="https://en.wikipedia.org/wiki/Markdown">MARKDOWN</a> files 
    as well as linked image galleries for <a href="http://docs.getpelican.com/en/stable/">PELICAN</a> blog posts.
    """

    def __init__(self, token_url, start_state_class, database, authorized_users=[]):
        super().__init__(token_url, start_state_class)
        self.__database = database
        self.__database.setup()

        if authorized_users is not None:
            for user_id in authorized_users:
                if not self.__database.get_users(user_id=user_id):
                    self.__database.add_user(user_id, True, self.get_start_state_class()(self))
                else:
                    self.__database.update_user(user_id, is_authorized=True)

        for user in self.__database.get_users(is_authorized=True):
            super().set_user_state(user["user_id"], user["state"](self))

    def set_user_state(self, user_id, state):
        if not self.__database.get_users(user_id=user_id):
            self.__database.add_user(user_id, False, self.get_start_state_class()(self))
        else:
            self.__database.update_user(user_id, state=state)

        super().set_user_state(user_id, state)

    def handle_update(self, update):
        user_id = telegram.get_update_sender_id(update)
        authorized_users = self.__database.get_users(user_id=user_id, is_authorized=True)

        if user_id is not None and len(authorized_users) == 1:
            super().handle_update(update)

        # TODO: maybe do something with updates from unauthorized users?
