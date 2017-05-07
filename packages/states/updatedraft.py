from packages.states.abstractstate import AbstractState
from packages.bot.parsemode import ParseMode
import packages.bot.telegram as telegram

__author__ = "aneanet"


class UpdateDraftState(AbstractState):
    """
    Concrete state implementation.
    """

    def __init__(self, context, chat_id=None, user_id=None):
        super().__init__(context)

        if chat_id is not None and user_id is not None:
            reply_options = []
            for post in self.get_context().get_posts(user_id=user_id, status="draft"):
                reply_options.append({"text": post["title"], "callback_data": "/updatedraft " + str(post["post_id"])})

            if len(reply_options) > 0:
                self.get_context().send_message(chat_id, "Which one of your drafts do you want to update?"
                                                , parse_mode=ParseMode.MARKDOWN.value
                                                , reply_markup=telegram.build_inline_keyboard(reply_options))
            else:
                self.get_context().send_message(chat_id, "There is nothing to update. You don't have any drafts."
                                                , parse_mode=ParseMode.MARKDOWN.value)

    def process_update(self, update):
        update_type = telegram.get_update_type(update)

        # --------------------------------------------------------------------------------------------------------------
        # message
        # --------------------------------------------------------------------------------------------------------------
        if update_type == "message":
            chat_id = update[update_type]["chat"]["id"]
            text = update[update_type]["text"].strip(' \t\n\r') if "text" in update[update_type] else None

            # ----------------------------------------------------------------------------------------------------------
            # user entered text
            # ----------------------------------------------------------------------------------------------------------
            if text:
                # for global commands simply run code of IdleState
                if text in ["/start", "/help", "/createdraft", "/updatedraft", "/deletedraft"] or text.startswith("/"):
                    from packages.states.idlestate import IdleState
                    IdleState(self.get_context()).process_update(update)
            else:
                self.get_context().send_message(chat_id, "Unrecognized command or message!"
                                                + "\r\n" + "Send /help to see available commands."
                                                , parse_mode=ParseMode.MARKDOWN.value)

        # --------------------------------------------------------------------------------------------------------------
        # callback query
        # --------------------------------------------------------------------------------------------------------------
        elif update_type == "callback_query":
            self.get_context().answer_callback_query(update[update_type]["id"])
            user_id = telegram.get_update_sender_id(update)
            chat_id = update[update_type]["message"]["chat"]["id"]
            message_id = update[update_type]["message"]["message_id"]
            data = update[update_type]["data"].strip(' \t\n\r') if "data" in update[update_type] else None

            # ----------------------------------------------------------------------------------------------------------
            # /updatedraft ... - only allowed callback command
            # ----------------------------------------------------------------------------------------------------------
            if data.startswith("/updatedraft"):
                command_array = data.split(" ")

                print(update)   # TODO remove print after code is finished
                # ------------------------------------------------------------------------------------------------------
                # /updatedraft <post_id> - to-be-updated post_id was chosen
                # ------------------------------------------------------------------------------------------------------
                if len(command_array) == 2:
                    None  # TODO

                # ------------------------------------------------------------------------------------------------------
                # /updatedraft <post_id> <command> - update post_id with command
                # ------------------------------------------------------------------------------------------------------
                elif len(command_array) == 3:
                    None # TODO

                # ------------------------------------------------------------------------------------------------------
                # /updatedraft ... - update has invalid number of parameters
                # ------------------------------------------------------------------------------------------------------
                else:
                    self.get_context().edit_message_text(chat_id, message_id
                                                         , "Unrecognized command or message!"
                                                         + "\r\n" + "Send /help to see available commands."
                                                         , parse_mode=ParseMode.MARKDOWN.value)

            # ----------------------------------------------------------------------------------------------------------
            # anything not starting with /updatedraft is considered invalid
            # ----------------------------------------------------------------------------------------------------------
            else:
                self.get_context().edit_message_text(chat_id, message_id
                                                     , "Unrecognized command or message!"
                                                     + "\r\n" + "Send /help to see available commands."
                                                     , parse_mode=ParseMode.MARKDOWN.value)

        # --------------------------------------------------------------------------------------------------------------
        # unsupported update type
        # --------------------------------------------------------------------------------------------------------------
        else:
            print("unsupported update type:", update_type)  # TODO change to log rather than print
