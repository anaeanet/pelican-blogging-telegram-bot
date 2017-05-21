from packages.states.idlestate import IdleState
from packages.bot.parsemode import ParseMode
import packages.bot.telegram as telegram

__author__ = "aneanet"


class CreateDraftState(IdleState):
    """
    Concrete state implementation.
    """

    def __init__(self, context, user_id, chat_id=None, message_id=None):
        super().__init__(context, user_id)

        if chat_id is not None:
            self.show_menu(user_id, chat_id, message_id=message_id)

    def show_menu(self, user_id, chat_id, message_id=None):
        reply_options = [{"text": "<< back to main menu", "callback_data": "/mainmenu"}]

        message_text = "Enter the *title* of your new draft:"
        if message_id is not None:
            self.get_context().edit_message_text(chat_id, message_id, message_text
                                                 , parse_mode=ParseMode.MARKDOWN.value
                                                 , reply_markup=telegram.build_inline_keyboard(reply_options))
        else:
            self.get_context().send_message(chat_id, message_id, message_text
                                            , parse_mode=ParseMode.MARKDOWN.value
                                            , reply_markup=telegram.build_inline_keyboard(reply_options))

    def process_callback_query(self, user_id, chat_id, message_id, data):
        command_array = data.split(" ")

        # abort draft creation and go back to main menu
        if len(command_array) == 1 and command_array[0] == "/mainmenu":
            self.get_context().set_user_state(user_id, IdleState(self.get_context(), user_id, chat_id=chat_id
                                                                 , message_id=message_id))

    def process_message(self, user_id, chat_id, text):
        if text.startswith("/"):
            super().process_message(user_id, chat_id, text)
        else:
            self.get_context().add_post(user_id, text)
            self.get_context().send_message(chat_id
                                            , "Successfully created draft '*" + text + "*'"
                                            , parse_mode=ParseMode.MARKDOWN.value)
            self.get_context().set_user_state(user_id, IdleState(self.get_context(), user_id, chat_id=chat_id))
