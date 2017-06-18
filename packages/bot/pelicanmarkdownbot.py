import packages.bot.telegram as telegram
import packages.bot.iohelper as iohelper
import os
from datetime import datetime
from packages.bot.abstractuserstatebot import AbstractUserStateBot
from packages.states.navigation.idlestate import IdleState
from packages.datamodel.poststate import PostState

import logging

__author__ = "anaeanet"


class PelicanMarkdownBot(AbstractUserStateBot):
    """
    This bot is a concrete implementation of a (user-state) telegram bot.
    It adds a persistence layer and only responds to authorized users.

    Its purpose is to create and maintain <a href="https://en.wikipedia.org/wiki/Markdown">MARKDOWN</a> files
    as well as linked image galleries for <a href="http://docs.getpelican.com/en/stable/">PELICAN</a> blog posts.
    """

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

            super().set_state(user.id, user_state)

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
        logger = logging.getLogger("pelicanblogbot").getChild("packages.bot.pelicanmarkdownbot.handle_update")

        user_id = telegram.get_update_sender_id(update)
        user = None if user_id is None else self.persistence.get_user(user_id)

        if user is not None:
            logger.debug(user.name + "/" + str(user.id)
                         + " (" + self.get_state(user.id).__class__.__name__ + ") -> "
                         + str(update[telegram.get_update_type(update)]))

            super().handle_update(update)
        else:
            logger.info("Unauthorized user '" + str(user_id) + "' interacting with bot: " + str(update))

    @staticmethod
    def __get_tmsp_and_filename(post, publish_type):

        # draft has never been fully published as post
        if post.original_post is None:
            # draft never published or already published as draft, respectively
            tmsp_publish = datetime.now() if post.tmsp_publish is None else post.tmsp_publish
        else:
            # draft is based on previously published post
            tmsp_publish = post.original_post.tmsp_publish

        file_name = tmsp_publish.strftime("%Y-%m-%d_%H-%M-%S") + ("_draft" if publish_type == PostState.DRAFT else "")
        return tmsp_publish, file_name

    @staticmethod
    def __build_pelican_post(post, tmsp_publish, gallery_file_name, publish_state):
        format_datetime_md = "%Y-%m-%d %H:%M"

        md_post = "Title: {}".format(post.title)

        # if draft is based on published post, use original post's date as publication date
        if post.original_post is not None:
            md_post += "\r\n" + "Date: {}".format(tmsp_publish.strftime(format_datetime_md))
            md_post += "\r\n" + "Modified: {}".format(datetime.now().strftime(format_datetime_md))
        else:
            md_post += "\r\n" + "Date: {}".format(datetime.now().strftime(format_datetime_md))

        # put author name into post, if author's name is provided
        if post.user.name is not None and len(post.user.name) > 0:
            md_post += "\r\n" + "Authors: {}".format(post.user.name)

        # tags
        if len(post.tags) > 0:
            md_post += "\r\n" + "Tags: {}".format(", ".join([tag.name for tag in post.tags]))

        # title image
        if post.title_image is not None:
            md_post += "\r\n" + "image: {photo}" + "{}".format(gallery_file_name) + "/" + "{}".format(post.title_image.name)

        # gallery
        if len(post.gallery.images) > 0:
            md_post += "\r\n" + "gallery: {photo}" + "{}".format(gallery_file_name) + "{" + post.gallery.title + "}"

        # status and content, separated by one empty line
        md_post += "\r\n" + "Status: {}".format(publish_state.value) \
                   + "\r\n\r\n" + post.content

        return md_post

    @staticmethod
    def __publish_locally(post, tmsp_publish, file_name, publish_state):

        # build content of markdown post file, then write to working directory
        markdown_post = PelicanMarkdownBot.__build_pelican_post(post, tmsp_publish, file_name, publish_state)
        is_published_locally = iohelper.write_to_file(file_name + ".md", "w", markdown_post)

        if is_published_locally and (post.title_image is not None or len(post.gallery.images) > 0):
            gallery_written = iohelper.create_folder(file_name)
            captions_written = iohelper.write_to_file(os.path.join(file_name, "captions.txt"), "w", "# captions.txt")

            images = post.gallery.images + ([post.title_image] if post.title_image is not None else [])
            for img in images:
                # stop processing if any of the files cannot be written
                if not (gallery_written and captions_written):
                    break

                gallery_written = gallery_written and iohelper.write_to_file(os.path.join(file_name, img.name), "wb", img.file)
                captions_written = captions_written and iohelper.write_to_file(os.path.join(file_name, "captions.txt"), "a"
                                                                               , "\r\n" + img.name + ":" + (img.caption if img.caption else img.name))

            # final result depends on successful processing of ALL images
            is_published_locally = gallery_written and captions_written

        return is_published_locally

    def publish(self, post_id, publish_state):
        logger = logging.getLogger("pelicanblogbot").getChild("packages.bot.pelicanmarkdownbot.publish")
        is_published = False

        post = self.persistence.get_post(post_id)
        if post is not None and publish_state in [state for state in PostState] and post.title and post.content:

            # fetch publication timestamp and derived filename, publish locally
            tmsp_publish, file_name = PelicanMarkdownBot.__get_tmsp_and_filename(post, publish_state)
            if self.__publish_locally(post, tmsp_publish, file_name, publish_state):

                # dry-run: update post with publish timestamp and new status
                updated_post = self.persistence.update_post(post.id, post.user.id, post.title, publish_state
                                                            , post.gallery.title, post.content
                                                            , None if post.title_image is None else post.title_image.id
                                                            , tmsp_publish
                                                            , None if post.original_post is None else post.original_post.id
                                                            , commit=False)

                if updated_post is not None:
                    is_published = iohelper.transfer_file(file_name + ".md", self.__post_target_url)

                    if is_published and (len(post.gallery.images) > 0 or post.title_image is not None):
                        is_published = iohelper.transfer_file(file_name, self.__gallery_target_url)
                    else:
                        # delete gallery folder from remote location (may never have existed in the first place)
                        if not iohelper.remove_file(os.path.join(self.__gallery_target_url, file_name)):
                            logger.warning("obsolete gallery '" + file_name + "' could not be removed from: " + self.__gallery_target_url)

                if is_published:
                    self.persistence.commit()

                    # remove draft files from remote location if this publicationa s post
                    if publish_state == PostState.PUBLISHED:
                        iohelper.remove_file(os.path.join(self.__post_target_url, file_name + "_draft.md"))
                        iohelper.remove_file(os.path.join(self.__gallery_target_url, file_name + "_draft"))

                else:
                    self.persistence.rollback()
                    logger.warning("publication of " + ("draft" if publish_state == PostState.DRAFT else "post")
                                   + "'" + post.title + "' failed and had to be rolled back.")

            # delete local files - markdown file and gallery folder
            if not (iohelper.remove_file(file_name + ".md") and iohelper.remove_file(file_name)):
                logger.warning("locally published files '" + file_name + "*' could not deleted.")

        return is_published

    def unpublish(self, post_id):
        logger = logging.getLogger("pelicanblogbot").getChild("packages.bot.pelicanmarkdownbot.unpublish")
        is_unpublished = False

        post = self.persistence.get_post(post_id)
        if post is not None:

            # a draft that was never published before is automatically unpublished
            if not post.tmsp_publish:
                is_unpublished = True

            # previously published draft or post
            else:

                # fetch publication timestamp, use it as filename
                tmsp_publish, file_name = PelicanMarkdownBot.__get_tmsp_and_filename(post, post.status)

                # remove published files (markdown and gallery) from target location
                markdown_unpublished = iohelper.remove_file(os.path.join(self.__post_target_url, file_name + ".md"))
                gallery_unpublished = iohelper.remove_file(os.path.join(self.__gallery_target_url, file_name))

                if markdown_unpublished and gallery_unpublished:
                    is_unpublished = True
                else:
                    logger.warning("'" + post.title + "' could not be unpublished")

        return is_unpublished
