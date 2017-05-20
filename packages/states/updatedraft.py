from packages.states.idlestate import IdleState
from packages.bot.parsemode import ParseMode
import packages.bot.telegram as telegram

__author__ = "aneanet"


class UpdateDraftState(IdleState):
    """
    Concrete state implementation.
    """

    def __init__(self, context, chat_id=None, user_id=None, message_id=None):
        super().__init__(context)

        if chat_id is not None and user_id is not None:
            reply_options = []
            for post in self.get_context().get_posts(user_id=user_id, status="draft"):
                reply_options.append({"text": post["title"], "callback_data": "/updatedraft " + str(post["post_id"])})

            if len(reply_options) > 0:
                if message_id is not None:
                    self.get_context().edit_message_text(chat_id, message_id,
                                                         "Which one of your drafts do you want to update?"
                                                        , parse_mode=ParseMode.MARKDOWN.value
                                                        , reply_markup=telegram.build_inline_keyboard(reply_options))
                else:
                    self.get_context().send_message(chat_id, "Which one of your drafts do you want to update?"
                                                    , parse_mode=ParseMode.MARKDOWN.value
                                                    , reply_markup=telegram.build_inline_keyboard(reply_options))
            else:
                self.get_context().send_message(chat_id, "There is nothing to update. You don't have any drafts."
                                                , parse_mode=ParseMode.MARKDOWN.value)

    def process_callback_query(self, user_id, chat_id, message_id, data):
        command_array = data.split(" ")

        # ------------------------------------------------------------------------------------------------------
        # /updatedraft <post_id> - to-be-updated post_id was chosen
        # ------------------------------------------------------------------------------------------------------
        if len(command_array) == 2:
            # TODO add more options: tags, images, ...
            reply_options = []
            post_title = None
            for post in self.get_context().get_posts(post_id=command_array[1], user_id=user_id, status="draft"):
                post_title = post["title"]
                if post["content"] is not None:
                    reply_options.append({"text": "edit content", "callback_data": data + " /editcontent"})
                reply_options.append({"text": "add content", "callback_data": data + " /addcontent"})
                reply_options.append({"text": "<< back to drafts", "callback_data": data + " /back"})

            if post_title is not None:
                self.get_context().edit_message_text(chat_id, message_id,
                                                     "What do you want to do with draft '*" + post_title + "*'?"
                                                     , parse_mode=ParseMode.MARKDOWN.value
                                                     , reply_markup=telegram.build_inline_keyboard(reply_options))
            else:
                self.get_context().edit_message_text(chat_id, message_id,
                                                     "The selected draft does not exist!"
                                                     , parse_mode=ParseMode.MARKDOWN.value)

        # ------------------------------------------------------------------------------------------------------
        # /updatedraft <post_id> <command> - update post_id with command
        # ------------------------------------------------------------------------------------------------------
        elif len(command_array) == 3:

            # go back to let user select draft-to-be-updated once more
            if command_array[2] == "/back":
                self.get_context().set_user_state(user_id, UpdateDraftState(self.get_context(), chat_id=chat_id
                                                                            , user_id=user_id, message_id=message_id))
            else:
                # TODO
                None

        # ------------------------------------------------------------------------------------------------------
        # /updatedraft ... - invalid number of parameters
        # ------------------------------------------------------------------------------------------------------
        else:
            self.notify_invalid_command(chat_id)

    def process_update(self, update):
        print(update) # TODO delete print once state is finished
        update_type = telegram.get_update_type(update)

        if update_type == "callback_query":
            self.get_context().answer_callback_query(update[update_type]["id"])
            user_id = telegram.get_update_sender_id(update)
            chat_id = update[update_type]["message"]["chat"]["id"]
            message_id = update[update_type]["message"]["message_id"]
            data = update[update_type]["data"].strip(' \t\n\r') if "data" in update[update_type] else None

            if data.startswith("/updatedraft"):
                self.process_callback_query(user_id, chat_id, message_id, data)
            else:
                self.notify_invalid_command(chat_id)

        else:
            super().process_update(update)
