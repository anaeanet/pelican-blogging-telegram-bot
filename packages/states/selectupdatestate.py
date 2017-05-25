from packages.states.idlestate import IdleState
from packages.bot.parsemode import ParseMode
import packages.bot.telegram as telegram

__author__ = "aneanet"


class SelectUpdateState(IdleState):
    """
    Concrete state implementation.
    """

    def __init__(self, context, user_id, post_id, chat_id=None, message_id=None):
        self.__post_id = post_id # TODO serialize this attribute
        super().__init__(context, user_id, chat_id=chat_id, message_id=message_id)

    @property
    def post_id(self):
        return self.__post_id

    @property
    def init_message(self):
        message = "It seems the draft you selected no longer exists..."
        user_drafts = self.context.get_posts(post_id=self.post_id, status="draft")
        if len(user_drafts) > 0:
            post_title = user_drafts[0]["title"]
            message = "What do you want to do with draft '*" + post_title + "*'?"
        return message

    @property
    def initial_options(self):
        reply_options = [{"text": "<< drafts", "callback_data": "/updatedraft"}]

        user_drafts = self.context.get_posts(post_id=self.post_id, user_id=self.user_id, status="draft")
        if len(user_drafts) > 0:
            reply_options.append({"text": "EDIT content", "callback_data": "/selectupdate /editcontent"})
            # TODO add more options here
        reply_options.append({"text": "<< main menu", "callback_data": "/mainmenu"})

        return reply_options

    def build_state_message(self, chat_id, message_text, message_id=None, reply_options=None, keyboard_columns=2):
        super().build_state_message(chat_id, message_text, message_id=message_id, reply_options=reply_options, keyboard_columns=keyboard_columns)

    def process_callback_query(self, user_id, chat_id, message_id, data):
        command_array = data.split(" ")

        # only accept "/selectupdate ..." callback queries, have super() handle everything else
        if len(command_array) > 1 and command_array[0] == "/selectupdate":

            # update-option was chosen for selected draft - /selectupdate <update-option>
            if len(command_array) == 2:

                if command_array[1] == "/editcontent":
                    # TODO
                    None

                # TODO add other update options

        else:
            super().process_callback_query(user_id, chat_id, message_id, data)
