from packages.states.idlestate import IdleState
from packages.bot.parsemode import ParseMode
import packages.bot.telegram as telegram

__author__ = "aneanet"


class CreateDraftState(IdleState):
    """
    Concrete state implementation.
    """

    def show_menu(self, user_id, chat_id, message_id=None):
        reply_options = [{"text": "<< main menu", "callback_data": "/mainmenu"}]

        message_text = "Enter the *title* of your new draft:"
        if message_id is not None:
            self.context.edit_message_text(chat_id, message_id, message_text
                                                 , parse_mode=ParseMode.MARKDOWN.value
                                                 , reply_markup=telegram.build_inline_keyboard(reply_options))
        else:
            self.context.send_message(chat_id, message_id, message_text
                                            , parse_mode=ParseMode.MARKDOWN.value
                                            , reply_markup=telegram.build_inline_keyboard(reply_options))

    def process_message(self, user_id, chat_id, text):
        if text.startswith("/"):
            super().process_message(user_id, chat_id, text)
        else:
            self.context.add_post(user_id, text)
            self.context.send_message(chat_id
                                            , "Successfully created draft '*" + text + "*'"
                                            , parse_mode=ParseMode.MARKDOWN.value)
            user_state = IdleState(self.context, user_id, chat_id=chat_id)
            self.context.set_user_state(user_id, user_state)
