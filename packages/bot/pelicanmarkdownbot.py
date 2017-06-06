from packages.bot.abstractuserstatebot import AbstractUserStateBot
from packages.states.navigation.idlestate import IdleState
from packages.datamodel.tag import Tag
from packages.datamodel.image import Image
from packages.datamodel.gallery import Gallery
from packages.datamodel.poststate import PostState
from packages.datamodel.post import Post
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

    # --- following message act as intermediary wrappers for states changing db data ---

    def get_user_posts(self, user_id, status=None):
        user_posts = []

        posts = self.__database.get_posts(user_id=user_id, status=status.value)
        for post in posts:

            # fetch tags, gallery, and title image assigned to current post
            tags = self.get_post_tags(post["post_id"])
            title_image = self.get_post_title_image(post["post_id"])
            gallery = self.get_post_gallery(post["post_id"])

            user_posts.append(Post(post["post_id"], post["title"], PostState(post["status"])
                                    , content=post["content"]
                                    , tags=tags
                                    , title_image=title_image
                                    , gallery=gallery))

        return user_posts

    def get_post(self, post_id):
        post = None

        posts = self.__database.get_posts(post_id=post_id)
        if len(posts) == 1:
            p = posts[0]

            # fetch tags, gallery, and title image assigned to current post
            tags = self.get_post_tags(post_id)
            title_image = self.get_post_title_image(post_id)
            gallery = self.get_post_gallery(post_id)

            post = Post(p["post_id"], p["title"], PostState(p["status"])
                        , content=p["content"]
                        , tags=tags
                        , title_image=title_image
                        , gallery=gallery)

        return post

    def create_post(self, user_id, title, status):
        post = None

        from datetime import datetime
        post_id = self.__database.add_post(user_id, title, status=status.value, gallery_title="Bildergalerie", tmsp_create=datetime.now(), content="", title_image=None, tmsp_publish=None, original_post_id=None)

        if post_id:
            post = self.get_post(post_id)

        return post

    def update_post(self, post_id, title=None, content=None, gallery_title=None):
        updated_post = None

        if self.__database.update_post(post_id, title=title, content=content, gallery_title=gallery_title) > 0:
            updated_post = self.get_post(post_id)

        return updated_post

    def delete_post(self, post_id):
        deleted_post = None

        post = self.get_post(post_id)
        if post is not None:

            # remove tags from post
            for tag in post.tags:
                deleted_tag = self.delete_post_tag(post.id, tag.id)

            # remove reference to title image from post
            if post.title_image is not None:
                deleted_title_image = self.delete_post_title_image(post.id)

            # remove all links to images from post
            for image in post.gallery.images + ([post.title_image] if post.title_image is not None else []):
                deleted_image = self.delete_post_image(post.id, image.id)

            # delete post itself
            if self.__database.delete_post(post.id) > 0:
                deleted_post = post

        return deleted_post

    def get_post_tags(self, post_id):
        user_post_tags = []

        post_tags = self.__database.get_post_tags(post_id=post_id)
        for draft_tag in post_tags:

            tags = self.__database.get_tags(tag_id=draft_tag["tag_id"])
            for tag in tags:
                user_post_tags.append(Tag(tag["tag_id"], tag["name"]))

        return user_post_tags

    def add_post_tag(self, post_id, name):
        tag = None

        post = self.get_post(post_id)
        if post is not None:

            # check if tag is not already part of post's tag list
            if name not in [tag.name for tag in post.tags]:

                # check if tag exists at all, if not -> add to db
                tags = self.__database.get_tags(name=name)
                if len(tags) == 0:
                    tag_id = self.__database.add_tag(name)
                else:
                    tag_id = tags[0]["tag_id"]

                # link tag with post
                if tag_id > 0:
                    post_tag_id = self.__database.add_post_tag(post.id, tag_id)

                    if post_tag_id > 0:
                        tag = Tag(tag_id, name)

        return tag

    def delete_post_tag(self, post_id, tag_id):
        deleted_tag = None

        post = self.get_post(post_id)
        if post is not None:

            # check if tag is part of post's tag list
            for tag in post.tags:

                # ignore tags with "wrong" tag_id
                if str(tag.id) != str(tag_id):
                    continue
                else:

                    post_tags = self.__database.get_post_tags(post_id=post.id, tag_id=tag.id)
                    if len(post_tags) == 1:
                        post_tag_id = post_tags[0]["post_tag_id"]

                        # remove tag from post and return deleted tag
                        if self.__database.delete_post_tag(post_tag_id) > 0:
                            deleted_tag = tag

        # check if tag is used by any other draft, if not -> remove completely
        if len(self.__database.get_post_tags(tag_id=tag_id)) == 0:
            self.__database.delete_tag(tag_id=tag_id)

        return deleted_tag

    def get_post_gallery(self, post_id):
        post_gallery = None

        posts = self.__database.get_posts(post_id=post_id)
        if len(posts) == 1:
            post = posts[0]
            gallery_images = []

            post_images = self.__database.get_post_images(post_id=post_id)
            for post_image in post_images:

                images = self.__database.get_images(image_id=post_image["image_id"])
                for image in images:

                    img = Image(image["image_id"]
                                , image["file_name"], image["file_id"], image["file"]
                                , thumb_id=image["thumb_id"], caption=post_image["caption"])

                    if post_image["post_image_id"] != post["title_image"]:
                        gallery_images.append(img)

            post_gallery = Gallery(post["gallery_title"], gallery_images)

        return post_gallery

    def add_post_image(self, post_id, file_name, file_id, thumb_id=None, caption=None):
        image = None

        post = self.get_post(post_id)
        if post is not None:

            # check if image is not already part of post's gallery or title image
            if file_id not in [image.file_id for image in
                               post.gallery.images + ([post.title_image] if post.title_image is not None else [])]:

                # check if image exists at all, if not -> add to db
                images = self.__database.get_images(file_id=file_id)
                if len(images) == 0:
                    image_id = 0

                    # TODO move this code somewhere else?

                    # get telegram "File" via file_id, then download actual image
                    file = None
                    telegram_file = self.get_file(file_id)
                    if "result" in telegram_file and "file_path" in telegram_file["result"]:
                        file_url = telegram_file["result"]["file_path"]
                        file_name += "." + file_url.rsplit(".", 1)[1]
                        file = self.download_file(file_url)

                    if file is not None:
                        image_id = self.__database.add_image(file_name, file_id, file, thumb_id=thumb_id)

                else:
                    image_id = images[0]["image_id"]

                # link image with post
                if image_id > 0:
                    post_image_id = self.__database.add_post_image(post.id, image_id, caption=caption)

                    if post_image_id > 0:
                        image = Image(image_id, file_name, file_id, file, thumb_id=thumb_id, caption=caption)

        return image

    def delete_post_image(self, post_id, image_id):
        deleted_image = None

        post = self.get_post(post_id)
        if post is not None:

            # check if image is part of post's gallery or title image
            for image in post.gallery.images + ([post.title_image] if post.title_image is not None else []):

                # ignore images with "wrong" post_image_id
                if str(image.id) != str(image_id):
                    continue
                else:

                    post_images = self.__database.get_post_images(post_id=post.id, image_id=image.id)
                    if len(post_images) == 1:
                        post_image_id = post_images[0]["post_image_id"]

                        # if image is post's title image, remove reference
                        if post.title_image is not None and post.title_image.id == image.id:
                            self.__database.delete_title_image(post.id)

                        # remove image from post and return deleted image
                        if self.__database.delete_post_image(image.id) > 0:
                            deleted_image = Image(image.id, image.name, image.file_id, image.file, thumb_id=image.thumb_id, caption=image.caption)

        # check if image is used by any other draft, if not -> remove completely
        if len(self.__database.get_post_images(image_id=image_id)) == 0:
            self.__database.delete_image(image_id=image_id)

        return deleted_image

    def get_post_title_image(self, post_id):
        post_title_image = None

        posts = self.__database.get_posts(post_id=post_id)
        if len(posts) == 1:
            post = posts[0]

            post_image_id = post["title_image"]
            if post_image_id is not None:

                post_images = self.__database.get_post_images(post_image_id=post_image_id)
                if len(post_images) == 1:
                    post_image = post_images[0]

                    images = self.__database.get_images(image_id=post_image["image_id"])
                    if len(images) == 1:
                        image = images[0]

                        post_title_image = Image(image["image_id"]
                                                , image["file_name"], image["file_id"], image["file"]
                                                , thumb_id=image["thumb_id"], caption=post_image["caption"])

        return post_title_image

    def set_post_title_image(self, post_id, image_id):
        title_image = None

        post = self.get_post(post_id)
        if post is not None:

            # ensure that title image is already part of post's gallery
            for image in post.gallery.images:

                # ignore "wrong" images
                if str(image.id) != str(image_id):
                    continue
                else:

                    post_images = self.__database.get_post_images(post_id=post.id, image_id=image.id)
                    if len(post_images) == 1:
                        post_image_id = post_images[0]["post_image_id"]

                        if self.__database.update_post(post.id, title_image=post_image_id) > 0:
                            title_image = image

        return title_image

    def delete_post_title_image(self, post_id):
        deleted_image = None

        post = self.get_post(post_id)
        if post is not None:

            if post.title_image is not None and self.__database.delete_title_image(post_id) > 0:
                deleted_image = post.title_image

        return deleted_image