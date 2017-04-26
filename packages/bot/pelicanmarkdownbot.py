from packages.bot.abstractuserstatebot import AbstractUserStateBot

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

    def __process_authorized_users(self, authorized_users):
        # store all authorized users on database
        for user_id in authorized_users:
            if not self.__database.get_users(user_id=user_id):
                self.__database.add_user(user_id, True, self.get_start_state_class()(self))
            else:
                self.__database.update_user(user_id, is_authorized=True)

    def __load_user_states_from_database(self):
        #initialize statuses for all users on db
        for user in self.__database.get_users(is_authorized=True):
            self.set_user_state(user["user_id"], user["state"](self))

