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
        self.database.setup()

        # store all authorized users in database
        if authorized_users is not None:
            for user_id in authorized_users:
                if not self.database.get_users(user_id=user_id):
                    user_state = self.start_state_class(self, user_id)
                    self.database.add_user(user_id, True, user_state)
                else:
                    self.database.update_user(user_id, is_authorized=True)

        # load all authorized users from database into bot's user-state-dictionary
        for user in self.database.get_users(is_authorized=True):
            state_class, params = user["state_class"]
            user_id = user["user_id"]

            # TODO update if deserialize changes
            if "post_id" in params:
                user_state = state_class(self, user_id, params["post_id"], message_id=params["message_id"])
            else:
                user_state = state_class(self, user_id, message_id=params["message_id"])

            super().set_user_state(user_id, user_state)

    @property
    def database(self):
        return self.__database

    def set_user_state(self, user_id, state):
        if not self.database.get_users(user_id=user_id):
            user_state = self.start_state_class(self, user_id)
            self.database.add_user(user_id, False, user_state)
        else:
            self.database.update_user(user_id, state=state)

        super().set_user_state(user_id, state)

    def handle_update(self, update):
        user_id = telegram.get_update_sender_id(update)
        authorized_users = self.database.get_users(user_id=user_id, is_authorized=True)

        if user_id is not None and len(authorized_users) == 1:
            print(self.get_user_state(user_id).__class__.__name__, update[telegram.get_update_type(update)])  # TODO remove print
            super().handle_update(update)
        else:
            # TODO: maybe do something with updates from unauthorized users?
            None

    def get_posts(self, post_id=None, user_id=None, title=None, status=None, tmsp_create=None, content=None, title_image=None, tmsp_publish=None, original_post_id=None):
        return self.database.get_posts(post_id=post_id, user_id=user_id, title=title, status=status, tmsp_create=tmsp_create, content=content, title_image=title_image, tmsp_publish=tmsp_publish, original_post_id=original_post_id)

    def add_post(self, user_id, title, status=None, tmsp_create=None, content=None, title_image=None, tmsp_publish=None, original_post_id=None):
        self.database.add_post(user_id, title, status=status, tmsp_create=tmsp_create, content=content, title_image=title_image, tmsp_publish=tmsp_publish, original_post_id=original_post_id)

    def update_post(self, post_id, user_id=None, title=None, status=None, tmsp_create=None, content=None, title_image=None, tmsp_publish=None, original_post_id=None):
        self.database.update_post(post_id, user_id=user_id, title=title, status=status, tmsp_create=tmsp_create, content=content, title_image=title_image, tmsp_publish=tmsp_publish, original_post_id=original_post_id)

    def delete_post(self, post_id):
        self.database.delete_post(post_id)

    def get_tag(self, tag_id=None, name=None):
        return self.database.get_tag(tag_id=tag_id, name=name)

    def add_tag(self, name):
        self.database.add_tag(name)

    def delete_tag(self, tag_id):
        self.database.delete_tag(tag_id)

    def get_post_tag(self, post_id, name=None):
        post_tags = []

        # consider optional name-filter
        tag_id = None
        if name is not None:
            name_tags = self.get_tag(name=name)
            if len(name_tags) > 0:
                tag_id = name_tags[0]["tag_id"]

        post_tag_ids = [x["tag_id"] for x in self.database.get_post_tag(post_id=post_id, tag_id=tag_id)]
        for tag_id in post_tag_ids:
            post_tags += self.get_tag(tag_id=tag_id)

        return post_tags

    def add_post_tag(self, post_id, name):
        # add tag if if does not exist yet
        if name not in self.get_tag(name=name):
            self.add_tag(name)

        # add tag to post if not already done
        if name not in [x["name"] for x in self.get_post_tag(post_id)]:
            tags = self.get_tag(name=name)
            if len(tags) > 0:
                tag_id = tags[0]["tag_id"]
                self.database.add_post_tag(post_id, tag_id)

    def delete_post_tag(self, post_tag_id):
        self.database.delete_post_tag(post_tag_id)

    def get_post_image(self, post_image_id=None, post_id=None, file_id=None, file_name=None, caption=None):
        return self.database.get_post_image(post_image_id=post_image_id, post_id=post_id, file_id=file_id, file_name=file_name, caption=caption)

    def add_post_image(self, post_id=None, file_id=None, file_name=None, caption=None):
        self.database.get_post_image(post_id=post_id, file_id=file_id, file_name=file_name, caption=caption)

    def delete_post_image(self, post_image_id=None):
        self.database.get_post_image(post_image_id=post_image_id)
