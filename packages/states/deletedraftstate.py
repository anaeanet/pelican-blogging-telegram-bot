from packages.states.idlestate import IdleState
from packages.bot.parsemode import ParseMode
import packages.bot.telegram as telegram

__author__ = "aneanet"


class DeleteDraftState(IdleState):
    """
    Concrete state implementation.
    """

    def show_menu(self, user_id, chat_id, message_id=None):
        reply_options = []
        for post in self.context.get_posts(user_id=user_id, status="draft"):
            reply_options.append({"text": post["title"], "callback_data": "/deletedraft " + str(post["post_id"])})
        reply_options.append({"text": "<< main menu", "callback_data": "/mainmenu"})

        message_text = "Which one of your drafts do you want to *delete*?"
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

        # only accept "/deletedraft ..." callback queries, have super() handle everything else
        if len(command_array) > 1 and command_array[0] == "/deletedraft":

            # draft selected for deletion - /deletedraft <post_id>
            if len(command_array) == 2:
                post_id = command_array[1]
                user_drafts = self.context.get_posts(post_id=post_id, user_id=user_id, status="draft")

                if len(user_drafts) > 0:
                    post_title = user_drafts[0]["title"]
                    reply_options = [{"text": "<< drafts", "callback_data": command_array[0]}
                                     , {"text": "Yes, delete", "callback_data": data + " /confirm"}
                                     , {"text": "<< main menu", "callback_data": "/mainmenu"}]

                    self.context.edit_message_text(chat_id, message_id
                                                         , "Do you really want to delete draft '*" + post_title + "*'?"
                                                         , parse_mode=ParseMode.MARKDOWN.value
                                                         , reply_markup=telegram.build_inline_keyboard(reply_options
                                                                                                       , columns=2))
                # TODO do something with older message (only way that selected post_id does not exist)

            # deletion of draft confirmed or aborted - /deletedraft <post_id> <confirm/back>
            elif len(command_array) == 3:

                # confirmed draft deletion
                if command_array[2] == "/confirm":
                    post_id = command_array[1]
                    user_drafts = self.context.get_posts(post_id=post_id, user_id=user_id, status="draft")

                    if len(user_drafts) > 0:
                        post_title = user_drafts[0]["title"]
                        self.context.delete_post(command_array[1])
                        self.context.edit_message_text(chat_id, message_id
                                                             , "Successfully deleted draft '*" + post_title + "*'."
                                                             , parse_mode=ParseMode.MARKDOWN.value)

                        # show remaining drafts for deletion
                        if len(self.context.get_posts(user_id=user_id, status="draft")) > 0:
                            next_state = DeleteDraftState(self.context, user_id, chat_id=chat_id)
                        else:   # no remaining drafts -> automatically go back to main menu
                            next_state = IdleState(self.context, user_id, chat_id=chat_id)
                        self.context.set_user_state(user_id, next_state)

                    # TODO do something with older message (only way that selected post_id does not exist)

        else:
            super().process_callback_query(user_id, chat_id, message_id, data)
