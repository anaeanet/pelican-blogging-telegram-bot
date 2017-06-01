from packages.bot.parsemode import ParseMode
from packages.states.navigation.selectdraftupdatestate import SelectDraftUpdateState

__author__ = "aneanet"


class AddImageState(SelectDraftUpdateState):
    """
    Concrete state implementation.
    Accepts user-sent images and links then to a previously selected post.
    """

    @property
    def init_message(self):
        message = "It seems the draft you selected no longer exists..."

        user_drafts = self.context.get_posts(post_id=self.post_id)
        if len(user_drafts) > 0:
            post_title = user_drafts[0]["title"]
            message = "What *image(s)* do you want to add to draft *" + post_title + "*?"

            # add current post_tags to init_message
            post_images = self.context.get_post_images(post_id=self.post_id)
            if len(post_images) > 0:
                message += "\r\n\r\n" + "*Current image(s)*"
                for post_image in post_images:
                    file_name = post_image["file_name"]
                    caption = post_image["caption"]
                    message += "\r\n" + file_name + (" - " + caption if caption else "")

        return message

    @property
    def initial_options(self):
        reply_options = [{"text": "<< update options", "callback_data": "/selectupdate"}
                        , {"text": "<< drafts", "callback_data": "/updatedraft"}
                        , {"text": "<< main menu", "callback_data": "/mainmenu"}]
        return reply_options

    def process_photo_message(self, user_id, chat_id, file_name, file_id, thumb_id=None, caption=None):

        # remove inline keyboard from latest bot message (by leaving out reply_options parameter)
        self.build_state_message(chat_id, self.init_message, message_id=self.message_id)

        user_drafts = self.context.get_posts(post_id=self.post_id)
        if len(user_drafts) > 0:
            post_title = user_drafts[0]["title"]

            # get telegram "File" via file_id, then download actual image
            file = None
            telegram_file = self.context.get_file(file_id)
            if "result" in telegram_file and "file_path" in telegram_file["result"]:

                file_url = telegram_file["result"]["file_path"]
                file_name += "." + file_url.rsplit(".", 1)[1]
                file = self.context.download_file(file_url)

            post_image_id = None
            if file is not None:
                # link image with post and store corresponding record on db
                post_image_id = self.context.add_post_image(self.post_id, file_name, file_id, file, thumb_id=None, caption=caption)

            if post_image_id is not None:
                self.context.send_message(chat_id
                                          , "Image successfully added to draft *" + post_title + "*."
                                          , parse_mode=ParseMode.MARKDOWN.value)
            else:
                self.context.send_message(chat_id
                                          , "The sent image could not be added to draft *" + post_title + "*."
                                          , parse_mode=ParseMode.MARKDOWN.value)

            next_state = AddImageState(self.context, user_id, self.post_id, chat_id=chat_id)
            self.context.set_user_state(user_id, next_state)

        else:
            self.context.send_message(chat_id
                                      , "It seems the draft you selected no longer exists..."
                                      , parse_mode=ParseMode.MARKDOWN.value)

            # show remaining drafts for updating
            if len(self.context.get_posts(user_id=user_id, status="draft")) > 0:
                from packages.states.draft.updatedraftstate import UpdateDraftState
                next_state = UpdateDraftState(self.context, user_id, chat_id=chat_id)
            # no remaining drafts -> automatically go back to main menu
            else:
                from packages.states.navigation.idlestate import IdleState
                next_state = IdleState(self.context, user_id, chat_id=chat_id)

            self.context.set_user_state(user_id, next_state)
