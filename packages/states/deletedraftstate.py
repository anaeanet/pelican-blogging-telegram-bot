from packages.states.idlestate import IdleState
from packages.bot.parsemode import ParseMode
import packages.bot.telegram as telegram

__author__ = "aneanet"


class DeleteDraftState(IdleState):
    """
    Concrete state implementation.
    """

    def __init__(self, context, chat_id=None, user_id=None):
        super().__init__(context)

        if chat_id is not None and user_id is not None:
            reply_options = []
            for post in self.get_context().get_posts(user_id=user_id, status="draft"):
                reply_options.append({"text": post["title"], "callback_data": "/deletedraft " + str(post["post_id"])})

            if len(reply_options) > 0:
                self.get_context().send_message(chat_id, "Which one of your drafts do you want to delete?"
                                                , parse_mode=ParseMode.MARKDOWN.value
                                                , reply_markup=telegram.build_inline_keyboard(reply_options))
            else:
                self.get_context().send_message(chat_id, "There is nothing to delete. You don't have any drafts."
                                                , parse_mode=ParseMode.MARKDOWN.value)

    def process_callback_query(self, user_id, chat_id, message_id, data):
        command_array = data.split(" ")

        # ------------------------------------------------------------------------------------------------------
        # /deletedraft <post_id> - to-be-deleted post_id was chosen
        # ------------------------------------------------------------------------------------------------------
        if len(command_array) == 2:
            reply_options = [{"text": "No, abort", "callback_data": data + " N"}]
            post_title = None
            for post in self.get_context().get_posts(post_id=command_array[1], user_id=user_id, status="draft"):
                reply_options.append({"text": "Yes, confirm", "callback_data": data + " Y"})
                post_title = post["title"]

            if post_title is not None:
                self.get_context().edit_message_text(chat_id, message_id,
                                                     "Do you really want to delete draft '*" + post_title + "*'?"
                                                     , parse_mode=ParseMode.MARKDOWN.value
                                                     , reply_markup=telegram.build_inline_keyboard(reply_options))
            else:
                self.get_context().edit_message_text(chat_id, message_id,
                                                     "The selected draft does not exist!"
                                                     , parse_mode=ParseMode.MARKDOWN.value)

        # ------------------------------------------------------------------------------------------------------
        # /deletedraft <post_id> <Y/N> - deletion of post_id was either confirmed or aborted
        # ------------------------------------------------------------------------------------------------------
        elif len(command_array) == 3:
            post_title = None
            for post in self.get_context().get_posts(post_id=command_array[1], user_id=user_id, status="draft"):
                post_title = post["title"]

            if post_title is not None:
                if command_array[2] == "Y":
                    self.get_context().delete_post(command_array[1])
                    self.get_context().edit_message_text(chat_id, message_id,
                                                         "Successfully deleted draft '*" + post_title + "*'."
                                                         , parse_mode=ParseMode.MARKDOWN.value)
                else:
                    self.get_context().edit_message_text(chat_id, message_id,
                                                         "Deletion of draft '*" + post_title + "*' was aborted."
                                                         , parse_mode=ParseMode.MARKDOWN.value)
            else:
                self.get_context().edit_message_text(chat_id, message_id,
                                                     "The selected draft does not exist!"
                                                     , parse_mode=ParseMode.MARKDOWN.value)

        # ------------------------------------------------------------------------------------------------------
        # /deletedraft ... - invalid number of parameters
        # ------------------------------------------------------------------------------------------------------
        else:
            self.notify_invalid_command(chat_id)

    def process_update(self, update):
        update_type = telegram.get_update_type(update)

        if update_type == "callback_query":
            self.get_context().answer_callback_query(update[update_type]["id"])
            user_id = telegram.get_update_sender_id(update)
            chat_id = update[update_type]["message"]["chat"]["id"]
            message_id = update[update_type]["message"]["message_id"]
            data = update[update_type]["data"].strip(' \t\n\r') if "data" in update[update_type] else None

            if data.startswith("/deletedraft"):
                self.process_callback_query(user_id, chat_id, message_id, data)
            else:
                self.notify_invalid_command(chat_id)

        else:
            super().process_update(update)
