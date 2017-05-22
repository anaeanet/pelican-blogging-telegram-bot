from packages.states.idlestate import IdleState
from packages.bot.parsemode import ParseMode
import packages.bot.telegram as telegram

__author__ = "aneanet"


class UpdateDraftState(IdleState):
    """
    Concrete state implementation.
    """

    def show_menu(self, user_id, chat_id, message_id=None):
        reply_options = []
        for post in self.context.get_posts(user_id=user_id, status="draft"):
            reply_options.append({"text": post["title"], "callback_data": "/updatedraft " + str(post["post_id"])})
        reply_options.append({"text": "<< main menu", "callback_data": "/mainmenu"})

        message_text = "Which draft do you want to *update*?"
        if message_id is not None:
            self.context.edit_message_text(chat_id, message_id, message_text
                                                 , parse_mode=ParseMode.MARKDOWN.value
                                                 , reply_markup=telegram.build_inline_keyboard(reply_options))
        else:
            self.context.send_message(chat_id, message_text
                                            , parse_mode=ParseMode.MARKDOWN.value
                                            , reply_markup=telegram.build_inline_keyboard(reply_options))

    def process_callback_query(self, user_id, chat_id, message_id, data):
        command_array = data.split(" ")

        # only accept "/updatedraft ..." callback queries, have super() handle everything else
        if len(command_array) > 1 and command_array[0] == "/updatedraft":

            # draft selected for deletion - /deletedraft <post_id>
            if len(command_array) == 2:
                post_id = command_array[1]
                user_drafts = self.context.get_posts(post_id=post_id, user_id=user_id, status="draft")

                if len(user_drafts) > 0:
                    post_title = user_drafts[0]["title"]
                    reply_options = [{"text": "<< drafts", "callback_data": command_array[0]}
                                     , {"text": "EDIT content", "callback_data": data + " /editcontent"}
                                     # TODO add more options here
                                     , {"text": "<< main menu", "callback_data": "/mainmenu"}]

                    self.context.edit_message_text(chat_id, message_id
                                                         , "What do you want to do with draft '*" + post_title + "*'?"
                                                         , parse_mode=ParseMode.MARKDOWN.value
                                                         , reply_markup=telegram.build_inline_keyboard(reply_options
                                                                                                       , columns=2))
                    # TODO do something with older message (only way that selected post_id does not exist)

            # deletion of draft confirmed or aborted - /deletedraft <post_id> <confirm/back>
            elif len(command_array) == 3:

                if command_array[2] == "/editcontent":
                    # TODO
                    None

                # TODO add other update options

        else:
            super().process_callback_query(user_id, chat_id, message_id, data)
