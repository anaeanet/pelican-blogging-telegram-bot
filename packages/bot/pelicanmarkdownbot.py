from packages.bot.abstractuserstatebot import AbstractUserStateBot
from packages.states.navigation.idlestate import IdleState
import packages.bot.telegram as telegram

__author__ = "anaeanet"


class PelicanMarkdownBot(AbstractUserStateBot):
    """
    This bot is a concrete implementation of a (user-state) telegram bot.
    It adds a persistence layer and only responds to authorized users.
    
    Its purpose is to create and maintain <a href="https://en.wikipedia.org/wiki/Markdown">MARKDOWN</a> files 
    as well as linked image galleries for <a href="http://docs.getpelican.com/en/stable/">PELICAN</a> blog posts.
    """

    def __init__(self, token_url, file_token_url, database, authorized_users=[]):
        super().__init__(token_url, file_token_url, IdleState)
        self.__database = database
        self.__database.setup()

        # store all authorized users in database
        if authorized_users is not None:
            for user_id in authorized_users:
                if not self.__database.get_users(user_id=user_id):
                    user_state = self.start_state_class(self, user_id)
                    self.__database.add_user(user_id, user_state)

        # load all users from database into bot's user-state-dictionary
        for user in self.__database.get_users():
            state_class, params = user["state_class"]
            user_id = user["user_id"]

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

                user_state = state_class(self, user_id, post_id, message_id=message_id)
            else:
                user_state = state_class(self, user_id, message_id=message_id)

            super().set_state(user_id, user_state)

    def set_state(self, user_id, state):
        if not self.__database.get_users(user_id=user_id):
            user_state = self.start_state_class(self, user_id)
            self.__database.add_user(user_id, False, user_state)
        else:
            self.__database.update_user(user_id, state=state)

        super().set_state(user_id, state)

    def handle_update(self, update):
        user_id = telegram.get_update_sender_id(update)
        authorized_users = self.__database.get_users(user_id=user_id)

        if user_id is not None and len(authorized_users) == 1:
            print(self.get_state(user_id).__class__.__name__, update[telegram.get_update_type(update)])  # TODO remove print
            super().handle_update(update)
        else:
            # TODO: maybe do something with updates from unauthorized users?
            None

    def get_posts(self, post_id=None, user_id=None, title=None, status=None, gallery_title=None, tmsp_create=None, content=None, title_image=None, tmsp_publish=None, original_post_id=None):
        return self.__database.get_posts(post_id=post_id, user_id=user_id, title=title, status=status, gallery_title=gallery_title, tmsp_create=tmsp_create, content=content, title_image=title_image, tmsp_publish=tmsp_publish, original_post_id=original_post_id)

    def add_post(self, user_id, title, status=None, gallery_title=None, tmsp_create=None, content=None, title_image=None, tmsp_publish=None, original_post_id=None):
        return self.__database.add_post(user_id, title, status=status, gallery_title=gallery_title, tmsp_create=tmsp_create, content=content, title_image=title_image, tmsp_publish=tmsp_publish, original_post_id=original_post_id)

    def update_post(self, post_id, user_id=None, title=None, status=None, gallery_title=None, tmsp_create=None, content=None, title_image=None, tmsp_publish=None, original_post_id=None):
        return self.__database.update_post(post_id, user_id=user_id, title=title, status=status, gallery_title=gallery_title, tmsp_create=tmsp_create, content=content, title_image=title_image, tmsp_publish=tmsp_publish, original_post_id=original_post_id)

    def delete_post(self, post_id):
        # delete any existing tags from post
        post_tags = self.__database.get_post_tags(post_id=post_id)
        for post_tag in post_tags:
            self.delete_post_tag(post_tag["post_tag_id"])

        # delete any existing images from post
        post_images = self.__database.get_post_images(post_id=post_id)
        for post_image in post_images:
            self.delete_post_image(post_image["post_image_id"])

        return self.__database.delete_post(post_id)

    def publish_post(self, post_id, status, tmsp_publish):
        result = 0

        # mark post as published at publish_date
        # TODO self.__database.update_post(post_id, status=status, tmsp_publish=tmsp_publish)

        # retrieve to-be-published post and make sure that minimal attributes have values, i.e. title & content
        posts = self.__database.get_posts(post_id=post_id)
        if len(posts) == 1 and len(posts[0]["title"]) > 0 and len(posts[0]["content"]) > 0:
            post = posts[0]

            # add title row to markdown file
            pelican_post = "Title: " + post["title"]

            # image folder name and name of *.md file
            timestamp = tmsp_publish.strftime("%Y-%m-%d_%H-%M-%S")

            # add date row to markdown file
            pelican_post += "\r\n" + "Date: " + tmsp_publish.strftime("%Y-%m-%d %H:%M")

            tag_names = []
            post_tags = self.__database.get_post_tags(post_id=post_id)
            for post_tag in post_tags:
                tags = self.__database.get_tags(post_tag["tag_id"])
                if len(tags) > 0:
                    tag_names.append(tags[0]["name"])

            # add tags row to markdown file
            if len(tag_names) > 0:
                pelican_post += "\r\n" + "Tags: " + ", ".join(tag_names)

            title_image = None
            gallery = None
            post_images = self.__database.get_post_images(post_id=post_id)
            if len(post_images) > (0 if post["title_image"] is None else 1):

                gallery = "{photo}" + timestamp + "{" + post["gallery_title"] + "}"

                for post_image in post_images:
                    if post_image["post_image_id"] == post["title_image"]:
                        title_image = "{photo}" + timestamp + "/" + post_image["file_name"]

            if title_image:
                pelican_post += "\r\n" + "image: " + title_image
            if gallery:
                pelican_post += "\r\n" + "gallery: " + gallery

            # add status row to markdown file
            pelican_post += "\r\n" + "Status: " + post["status"]
            # add content to markdown file
            pelican_post += "\r\n\r\n" + post["content"]

            pelican_file = open(timestamp + ".md", "w")
            pelican_file.write(pelican_post)

            if len(post_images) > 0:

                import os
                import errno
                try:
                    result = result and os.makedirs(timestamp)
                except OSError as exception:
                    if exception.errno != errno.EEXIST:
                        raise

                for image in post_images:
                    file = open(timestamp + "/" + image["file_name"], "wb")
                    result = result and file.write(image["file"])

                captions = open(timestamp + "/" + "captions.txt", "w")
                result = result and captions.write("\r\n".join([x["file_name"] + ":" + x["caption"] for x in post_images]))

        # if anything went wrong when attempting to publish, mark post as draft again on DB
        if result == 0:
            # TODO delete publish timestamp
            None #self.__database.update_post(post_id, status="draft", tmsp_publish=None)

        return result

    def get_tags(self, tag_id=None, name=None):
        return self.__database.get_tags(tag_id=tag_id, name=name)

    def add_tag(self, name):
        return self.__database.add_tag(name)

    def delete_tag(self, tag_id):
        return self.__database.delete_tag(tag_id)

    def get_post_tags(self, post_tag_id=None, post_id=None, tag_id=None):
        return self.__database.get_post_tags(post_tag_id=post_tag_id, post_id=post_id, tag_id=tag_id)

    def add_post_tag(self, post_id, tag_id):
        return self.__database.add_post_tag(post_id, tag_id)

    def delete_post_tag(self, post_tag_id):
        # get tag_id of the tag that is about to be removed from post
        tag_id = None
        post_tags = self.__database.get_post_tags(post_tag_id=post_tag_id)
        for post_tag in post_tags:
            tag_id = post_tag["tag_id"]

        result = self.__database.delete_post_tag(post_tag_id)

        # if tag was successfully remove from post, checkif it is used anywhere else, delete - if not
        post_tags_in_use = self.__database.get_post_tags(tag_id=tag_id)
        if result and len(post_tags_in_use) == 0:
                self.__database.delete_tag(tag_id)

        return result

    def get_post_images(self, post_image_id=None, post_id=None, file_name=None, file_id=None, file=None, thumb_id=None, caption=None):
        return self.__database.get_post_images(post_image_id=post_image_id, post_id=post_id, file_name=file_name, file_id=file_id, file=file, thumb_id=thumb_id, caption=caption)

    def add_post_image(self, post_id, file_name, file_id, file, thumb_id=None, caption=None):
        return self.__database.add_post_image(post_id, file_name, file_id, file, thumb_id=thumb_id, caption=caption)

    def delete_post_image(self, post_image_id):
        # delete any reference to image as post's title image
        posts = self.get_posts(title_image=post_image_id)
        for post in posts:
            self.delete_title_image(post["post_id"])

        return self.__database.delete_post_image(post_image_id)

    def delete_title_image(self, post_id):
        self.__database.delete_title_image(post_id)
