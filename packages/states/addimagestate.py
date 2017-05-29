from packages.states.selectdraftupdatestate import SelectDraftUpdateState
from packages.bot.parsemode import ParseMode
import re

__author__ = "aneanet"


class AddImageState(SelectDraftUpdateState):
    """
    Concrete state implementation.
    Accepts user-sent photos and links then to previously selected draft.
    """

    @property
    def init_message(self):
        message = "It seems the draft you selected no longer exists..."

        user_drafts = self.context.get_posts(post_id=self.post_id)
        if len(user_drafts) > 0:
            post_title = user_drafts[0]["title"]
            message = "What *image(s)* do you want to add to draft *" + post_title + "*?"

            # add current post_tags to init_message
            images = []
            post_image = self.context.get_post_images(post_id=self.post_id)
            for post_image in post_image:
                images.append(post_image["file_name"])

            if len(images) > 0:
                message += "\r\n\r\n" + "*Current images(s)*\r\n" + "\r\n".join(images)

        return message

    @property
    def initial_options(self):
        reply_options = [{"text": "<< update options", "callback_data": "/selectupdate"}
                        , {"text": "<< drafts", "callback_data": "/updatedraft"}
                        , {"text": "<< main menu", "callback_data": "/mainmenu"}]
        return reply_options

    def process_photo_message(self, user_id, chat_id, file_name, file_id, thumb_file_id=None, caption=None):

        # remove inline keyboard from latest bot message (by leaving out reply_options parameter)
        self.build_state_message(chat_id, self.init_message, message_id=self.message_id)

        # TODO

        next_state = AddImageState(self.context, user_id, self.post_id, chat_id=chat_id)
        self.context.set_user_state(user_id, next_state)
