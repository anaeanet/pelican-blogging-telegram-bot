from packages.states.idlestate import IdleState
from packages.bot.parsemode import ParseMode
import packages.bot.telegram as telegram

__author__ = "aneanet"


class CreateDraftState(IdleState):
    """
    Concrete state implementation.
    """

    def __init__(self, context, chat_id=None):
        super().__init__(context)

        if chat_id is not None:
            self.get_context().send_message(chat_id
                                            , "Enter the *title* of your new draft:"
                                            , parse_mode=ParseMode.MARKDOWN.value)

    def process_message(self, user_id, chat_id, text):

        # global commands
        if text in self.get_global_commands() or text.startswith("/"):
            super().process_message(user_id, chat_id, text)
        else:
            self.get_context().add_post(user_id, text)
            self.get_context().send_message(chat_id
                                            , "Successfully created draft '*" + text + "*'"
                                            , parse_mode=ParseMode.MARKDOWN.value)
            self.get_context().set_user_state(user_id, IdleState(self.get_context()))
