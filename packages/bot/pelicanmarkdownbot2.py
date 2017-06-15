import packages.bot.telegram as telegram
import packages.bot.iohelper as iohelper
import os
from datetime import datetime
from packages.bot.abstractuserstatebot import AbstractUserStateBot
from packages.states.navigation.idlestate import IdleState
from packages.datamodel.poststate import PostState

__author__ = "anaeanet"


class PelicanMarkdownBot2(AbstractUserStateBot):
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
        self.format_datetime_file_name = "%Y-%m-%d_%H-%M-%S"

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
        user_id = telegram.get_update_sender_id(update)
        user = self.persistence.get_user(user_id)

        if user_id is not None and user is not None:
            print(self.get_state(user_id).__class__.__name__,
                  update[telegram.get_update_type(update)])  # TODO remove print
            super().handle_update(update)
        else:
            # TODO: maybe do something with updates from unauthorized users?
            None

    def publish(self, post_id, publish_state):
        is_published = False

        post = self.persistence.get_post(post_id)
        if post is not None and publish_state in [state for state in PostState]:

            # get publication timestamp, depending on whether draft has been published before
            if post.original_post is None:
                if post.tmsp_publish is None:  # draft never published before
                    tmsp_publish = datetime.now()
                else:  # draft was published earlier (as draft)
                    tmsp_publish = post.tmsp_publish
            else:  # draft is based on previously published post
                original_post = self.persistence.get_post(post.original_post)
                tmsp_publish = original_post.tmsp_publish

            # use tmsp_publish as filename for blog post
            post_file_name = tmsp_publish.strftime(self.format_datetime_file_name)

            # build content of markdown post file
            format_datetime_md = "%Y-%m-%d %H:%M"
            md_post = "Title: {}".format(post.title)
            if post.original_post is not None:
                md_post += "\r\n" + "Date: {}".format(tmsp_publish.strftime(format_datetime_md))
                md_post += "\r\n" + "Modified: ".format(datetime.now().strftime(format_datetime_md))
            else:
                md_post += "\r\n" + "Date: {}".format(datetime.now().strftime(format_datetime_md))
            if post.user.name is not None and len(post.user.name) > 0:
                md_post += "\r\n" + "Authors: {}".format(post.user.name)
            if len(post.tags) > 0:
                md_post += "\r\n" + "Tags: {}".format(", ".join([tag.name for tag in post.tags]))
            if post.title_image is not None:
                md_post += "\r\n" + "image: {photo}" + "{}".format(post_file_name) + "/" + "{}".format(
                    post.title_image.name)
            if len(post.gallery.images) > 0:
                md_post += "\r\n" + "gallery: {photo}" + "{}".format(post_file_name) + "{" + post.gallery.title + "}"
            md_post += "\r\n" + "Status: {}".format(publish_state.value)
            md_post += "\r\n\r\n" + post.content

            # write markdown post file to working directory
            md_written = iohelper.write_to_file(post_file_name + ".md", "w", md_post)

            # if post file written successfully, process gallery and title image
            images = post.gallery.images + ([post.title_image] if post.title_image is not None else [])
            written_img_count = 0
            if md_written and len(images) > 0:
                gallery_written = iohelper.create_folder(post_file_name)
                captions_written = iohelper.write_to_file(os.path.join(post_file_name, "captions.txt"), "w",
                                                        "# captions.txt") if gallery_written else False

                # if gallery folder and captions.txt written successfully
                if gallery_written and captions_written:
                    for image in images:
                        image_written = iohelper.write_to_file(os.path.join(post_file_name, image.name), "wb", image.file)
                        image_caption_written = iohelper.write_to_file(os.path.join(post_file_name, "captions.txt"), "a",
                                                                     "\r\n" + image.name + ":" + image.caption)

                        if image_written and image_caption_written:
                            written_img_count += 1

            # if all file creation was successful, attempt to publish
            if md_written and written_img_count == len(images):
                rollback_tmsp_publish = post.tmsp_publish
                rollback_status = post.status

                updated_post = self.persistence.update_post(post.id, post.user.id, post.title, publish_state, post.gallery.title, post.content, post.title_image.id if post.title_image is not None else None, tmsp_publish, post.original_post)
                if updated_post is not None:
                    md_transfer_ok = iohelper.transfer_file(post_file_name + ".md", self.__post_target_url)
                    gallery_transfer_ok = iohelper.transfer_file(post_file_name, self.__gallery_target_url) if len(
                        images) > 0 else True

                    if len(images) == 0:
                        # delete gallery folder from remote location (may never have existed)
                        if not iohelper.remove_file(os.path.join(self.__post_target_url, post_file_name)):
                            # TODO log
                            None

                    # depending on file transfer, either mark post as successfully published or rollback
                    if md_transfer_ok and gallery_transfer_ok:
                        is_published = True
                    else:
                        self.persistence.update_post(post.id, post.user.id, post.title, rollback_status, post.gallery.title, post.content, post.title_image.id if post.title_image is not None else None, rollback_tmsp_publish, post.original_post)
                        # TODO log

            # delete local files - markdown file and gallery folder
            md_removed = iohelper.remove_file(post_file_name + ".md")
            gallery_removed = iohelper.remove_file(post_file_name)
            if not (md_removed and gallery_removed):
                # TODO log
                None

        return is_published

    def unpublish(self, post_id):
        is_unpublished = False

        post = self.persistence.get_post(post_id)
        if post is not None:

            # unpublish if draft/post was already published before
            if post.tmsp_publish is not None or post.original_post is not None:
                if post.tmsp_publish is not None:
                    timestamp = post.tmsp_publish
                else:
                    timestamp = self.persistence.get_post(post.original_post).tmsp_publish

                file_name = timestamp.strftime(self.format_datetime_file_name)

                # remove published files (markdown and gallery) from target location
                markdown_unpublished = iohelper.remove_file(os.path.join(self.__post_target_url, file_name + ".md"))
                gallery_unpublished = iohelper.remove_file(os.path.join(self.__gallery_target_url, file_name))

                if markdown_unpublished and gallery_unpublished:
                    is_unpublished = True
                else:
                    # TODO log
                    None

            # draft/post has never been published before
            else:
                is_unpublished = True

        return is_unpublished
