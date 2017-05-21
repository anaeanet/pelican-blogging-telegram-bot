from packages.states.idlestate import IdleState
from packages.bot.parsemode import ParseMode
import packages.bot.telegram as telegram

__author__ = "aneanet"


class DeleteDraftState(IdleState):
    """
    Concrete state implementation.
    """

    def __init__(self, context, user_id, chat_id=None, message_id=None):
        super().__init__(context, user_id)

        if chat_id is not None:
            self.show_menu(user_id, chat_id, message_id=message_id)

    def show_menu(self, user_id, chat_id, message_id=None):
        reply_options = []
        for post in self.get_context().get_posts(user_id=user_id, status="draft"):
            reply_options.append({"text": post["title"], "callback_data": "/deletedraft " + str(post["post_id"])})
        reply_options.append({"text": "<< back to main menu", "callback_data": "/mainmenu"})

        message_text = "Which one of your drafts do you want to delete?"
        if message_id is not None:
            self.get_context().edit_message_text(chat_id, message_id, message_text
                                                 , parse_mode=ParseMode.MARKDOWN.value
                                                 , reply_markup=telegram.build_inline_keyboard(reply_options))
        else:
            self.get_context().send_message(chat_id, message_text
                                            , parse_mode=ParseMode.MARKDOWN.value
                                            , reply_markup=telegram.build_inline_keyboard(reply_options))

    def process_callback_query(self, user_id, chat_id, message_id, data):
        command_array = data.split(" ")

        # abort draft deletion and go back to main menu
        if len(command_array) == 1 and command_array[0] == "/mainmenu":
            self.get_context().set_user_state(user_id, IdleState(self.get_context(), user_id, chat_id=chat_id
                                                                 , message_id=message_id))

        # draft chosen for deletion - /deletedraft <post_id>
        if len(command_array) == 2 and command_array[0] == "/deletedraft":

            post_id = command_array[1]
            user_drafts = self.get_context().get_posts(post_id=post_id, user_id=user_id, status="draft")

            if len(user_drafts) > 0:
                post_title = user_drafts[0]["title"]
                reply_options = [{"text": "<< back to drafts", "callback_data": data + " /back"}
                                 , {"text": "Yes, delete", "callback_data": data + " /confirm"}
                                 , {"text": "<< back to main menu", "callback_data": "/mainmenu"}]

                self.get_context().edit_message_text(chat_id, message_id
                                                     , "Do you really want to delete draft '*" + post_title + "*'?"
                                                     , parse_mode=ParseMode.MARKDOWN.value
                                                     , reply_markup=telegram.build_inline_keyboard(reply_options
                                                                                                   , columns=2))
            else:
                # TODO ??? only needed if older message is clicked
                self.get_context().edit_message_text(chat_id, message_id
                                                    , "The selected draft does not exist (anymore)!"
                                                    , parse_mode=ParseMode.MARKDOWN.value)

        # ------------------------------------------------------------------------------------------------------
        # /deletedraft <post_id> <Y/N> - deletion of post_id was either confirmed or aborted
        # ------------------------------------------------------------------------------------------------------
        elif len(command_array) == 3 and command_array[0] == "/deletedraft":

            # confirmed draft deletion
            if command_array[2] == "/confirm":

                post_id = command_array[1]
                user_drafts = self.get_context().get_posts(post_id=post_id, user_id=user_id, status="draft")

                if len(user_drafts) > 0:
                    post_title = user_drafts[0]["title"]
                    self.get_context().delete_post(command_array[1])
                    self.get_context().edit_message_text(chat_id, message_id
                                                         , "Successfully deleted draft '*" + post_title + "*'."
                                                         , parse_mode=ParseMode.MARKDOWN.value)
                    self.get_context().set_user_state(user_id, DeleteDraftState(self.get_context(), user_id
                                                                                , chat_id=chat_id))

                else:
                    # TODO ??? only needed if older message is clicked
                    self.get_context().edit_message_text(chat_id, message_id,
                                                         "The selected draft does not exist (anymore)!"
                                                         , parse_mode=ParseMode.MARKDOWN.value)

            # /back - return to draft list
            else:
                self.get_context().set_user_state(user_id, DeleteDraftState(self.get_context(), user_id
                                                                            , chat_id=chat_id, message_id=message_id))
