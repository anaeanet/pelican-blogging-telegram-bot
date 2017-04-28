from packages.states.abstractstate import AbstractState
from packages.bot.parsemode import ParseMode
import packages.bot.telegram as telegram

__author__ = "aneanet"


class UpdateDraftState(AbstractState):
    """
    Concrete state implementation.
    This class serves as start state for all users of "PelicanMarkdownBot".
    """

    def process_update(self, update):
        print(update)

        user_id = telegram.get_update_sender_id(update)
        update_type = telegram.get_update_type(update)

        if update_type == "message":
            chat_id = update["message"]["chat"]["id"]
            text = update[update_type]["text"].strip(' \t\n\r') if "text" in update[update_type] else None

            if text:
                # text message
                return

        from packages.states.idlestate import IdleState
        self.get_context().send_message(chat_id, "Unrecognized command or message!")
        self.get_context().set_user_state(user_id, IdleState(self.get_context()))