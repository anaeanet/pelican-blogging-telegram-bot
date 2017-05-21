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

        # store all authorized users in database
        if authorized_users is not None:
            for user_id in authorized_users:
                if not self.__database.get_users(user_id=user_id):
                    user_state = self.get_start_state_class()(self, user_id)
                    self.__database.add_user(user_id, True, user_state)
                else:
                    self.__database.update_user(user_id, is_authorized=True)

        # load all authorized users from database into bot's user-state-dictionary
        for user in self.__database.get_users(is_authorized=True):
            user_state = user["state_class"](self, user["user_id"])
            super().set_user_state(user["user_id"], user_state)

    def set_user_state(self, user_id, state):
        if not self.__database.get_users(user_id=user_id):
            user_state = self.get_start_state_class()(self, user_id)
            self.__database.add_user(user_id, False, user_state)
        else:
            self.__database.update_user(user_id, state=state)

        super().set_user_state(user_id, state)

    def handle_update(self, update):
        user_id = telegram.get_update_sender_id(update)
        authorized_users = self.__database.get_users(user_id=user_id, is_authorized=True)

        if user_id is not None and len(authorized_users) == 1:
            print(self.get_user_state(user_id), update[telegram.get_update_type(update)])  # TODO remove print
            super().handle_update(update)
        else:
            # TODO: maybe do something with updates from unauthorized users?
            None

    def get_posts(self, post_id=None, user_id=None, title=None, status=None, tmsp_create=None, is_selected=None, content=None, tmsp_publish=None):
        return self.__database.get_posts(post_id=post_id, user_id=user_id, title=title, status=status, tmsp_create=tmsp_create, is_selected=is_selected, content=content, tmsp_publish=tmsp_publish)

    def deselect_user_posts(self, user_id):
        for post in self.get_posts(user_id=user_id, is_selected=True):
            self.update_post(post["post_id"], is_selected=False)

    def add_post(self, user_id, title, status=None, tmsp_create=None, is_selected=None, content=None, tmsp_publish=None):
        # if new post gets positive selection flag, deselect all other posts of same user
        if is_selected:
            self.deselect_user_posts(user_id)
        self.__database.add_post(user_id, title, status=status, tmsp_create=tmsp_create, is_selected=is_selected, content=content, tmsp_publish=tmsp_publish)

    def update_post(self, post_id, user_id=None, title=None, status=None, tmsp_create=None, is_selected=None, content=None, tmsp_publish=None):
        # if current post gets updated with positive selection flag, deselect all other posts of same user
        if is_selected:
            for post in self.get_posts(post_id=post_id):
                self.deselect_user_posts(post["user_id"])
                break
        self.__database.update_post(post_id, user_id=user_id, title=title, status=status, tmsp_create=tmsp_create, is_selected=is_selected, content=content, tmsp_publish=tmsp_publish)

    def delete_post(self, post_id):
        self.__database.delete_post(post_id)
