from packages.bot.parsemode import ParseMode
from packages.states.navigation.selectdraftupdatestate import SelectDraftUpdateState
from packages.datamodel.poststate import PostState

__author__ = "aneanet"


class AddImageState(SelectDraftUpdateState):
    """
    Concrete state implementation.

    Accepts user-sent images and links then to a previously selected post.
    """

    @property
    def welcome_message(self):
        message = "It seems the draft you selected no longer exists..."

        post = self.bot.persistence.get_post(self.post_id)
        if post is not None:
            message = "What <b>image(s)</b> do you want to <b>add</b> to draft <b>" + post.title + "</b>?"

            # add current images to init_message
            if len(post.gallery.images) > 0 or post.title_image is not None:
                message += "\r\n\r\n" + "<b>Current image(s)</b>"

                if post.title_image is not None:
                    message += "\r\n" + "[TITLE] " + post.title_image.name + (" - " + post.title_image.caption if post.title_image.caption else "")

                for image in post.gallery.images:
                    message += "\r\n" + image.name + (" - " + image.caption if image.caption else "")

        return message

    @property
    def callback_options(self):
        # add buttons to return to update option menu, draft list, or main menu
        return [{"text": "<< update options", "callback_data": "/selectupdate"}
            , {"text": "<< drafts", "callback_data": "/updatedraft"}
            , {"text": "<< main menu", "callback_data": "/mainmenu"}]

    def process_photo_message(self, user_id, chat_id, file_id, thumb_id=None, caption=None):
        next_state = self

        # remove inline keyboard from latest bot message (by leaving out reply_options parameter)
        self.build_state_message(chat_id, self.welcome_message, message_id=self.message_id)

        # check if previously selected post still exists
        post = self.bot.persistence.get_post(self.post_id)
        if post is not None:

            image = None
            # TODO move this code to bot? -> file = self.context.download_file(file_id)
            telegram_file = self.bot.get_file(file_id)
            if "result" in telegram_file and "file_path" in telegram_file["result"]:
                file_url = telegram_file["result"]["file_path"]
                file = self.bot.download_file(file_url)

                if file is not None:
                    file_name = str(self.message_id) + "." + file_url.rsplit(".", 1)[1]
                    image = self.bot.persistence.add_post_image(post.id, file_id, file_name, file, thumb_id=thumb_id, caption=caption)

            if image is not None:
                self.bot.send_message(chat_id
                                      , "Image <b>" + image.name + "</b> has been <b>added</b> to draft <b>" + post.title + "</b>."
                                      , parse_mode=ParseMode.HTML.value)
            else:
                self.bot.send_message(chat_id
                                      , "<b>Image not added</b> to draft <b>" + post.title + "</b>."
                                      , parse_mode=ParseMode.HTML.value)

            next_state = AddImageState(self.bot, user_id, post.id, chat_id=chat_id)

        # previously selected post no longer exists
        else:
            self.bot.send_message(chat_id
                                  , "It seems the draft you selected no longer exists..."
                                  , parse_mode=ParseMode.HTML.value)

            # show remaining drafts for updating
            user_drafts = self.bot.get_user_posts(user_id=user_id, status=PostState.DRAFT)
            if len(user_drafts) > 0:
                from packages.states.draft.updatedraftstate import UpdateDraftState
                next_state = UpdateDraftState(self.bot, user_id, chat_id=chat_id)
            # no remaining drafts -> automatically go back to main menu
            else:
                from packages.states.navigation.idlestate import IdleState
                next_state = IdleState(self.bot, user_id, chat_id=chat_id)

        return next_state
