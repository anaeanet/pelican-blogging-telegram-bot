import packages.bot.telegram as telegram
from packages.bot.abstractuserstatebot import AbstractUserStateBot
from packages.states.navigation.idlestate import IdleState

__author__ = "anaeanet"


class PelicanMarkdownBot2(AbstractUserStateBot):
    """
    This bot is a concrete implementation of a (user-state) telegram bot.
    It adds a persistence layer and only responds to authorized users.

    Its purpose is to create and maintain <a href="https://en.wikipedia.org/wiki/Markdown">MARKDOWN</a> files
    as well as linked image galleries for <a href="http://docs.getpelican.com/en/stable/">PELICAN</a> blog posts.
    """

    format_datetime_db = "%Y-%m-%d %H:%M:%S.%f"
    format_datetime_file_name = "%Y-%m-%d_%H-%M-%S"
    format_datetime_md = "%Y-%m-%d %H:%M"

    def __init__(self, token, url, file_url, database, post_target_url, gallery_target_url, authorized_users=[]):
        super().__init__(token, url, file_url, IdleState)
        self.__database = database
        self.__database.setup()
        self.__post_target_url = post_target_url + ("/" if not post_target_url.endswith("/") else "")
        self.__gallery_target_url = gallery_target_url + ("/" if not gallery_target_url.endswith("/") else "")

        # store all authorized users in database
        if authorized_users is not None:
            for user in authorized_users:
                user_id = user["id"]
                user_name = user["name"] if "name" in user else None

                if self.persistence.get_user(user_id) is None:
                    user_state = self.start_state_class(self, user_id)
                    self.persistence.add_user(user_id, user_state, name=user_name)

        # load all users from database into bot's user-state-dictionary
        for user in self.persistence.get_users():
            state_class, params = user.state_class

            # load message_id from serialized param dict
            value = params["message_id"]
            if value != "None":
                message_id = int(value)
            else:
                message_id = None

            if "post_id" in params:
                # load post_id from serialized param dict
                value = params["post_id"]
                if value != "None":
                    post_id = int(value)
                else:
                    post_id = None

                user_state = state_class(self, user.id, post_id, message_id=message_id)
            else:
                user_state = state_class(self, user.id, message_id=message_id)

            super().set_state(user.id, user_state, name=user.name)

    @property
    def persistence(self):
        return self.__database

    def set_state(self, user_id, state, name=None):
        if self.persistence.get_user(user_id) is None:
            user_state = self.start_state_class(self, user_id)
            self.persistence.add_user(user_id, user_state, name=name)
        else:
            self.persistence.update_user(user_id, state, name)

        super().set_state(user_id, state)

    def handle_update(self, update):
        user_id = telegram.get_update_sender_id(update)
        user = self.persistence.get_user(user_id)

        if user_id is not None and user is not None:
            print(self.get_state(user_id).__class__.__name__,
                  update[telegram.get_update_type(update)])  # TODO remove print
            super().handle_update(update)
        else:
            # TODO: maybe do something with updates from unauthorized users?
            None
