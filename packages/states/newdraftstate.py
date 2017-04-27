from packages.states.abstractstate import AbstractState
import packages.bot.telegram as telegram

__author__ = "aneanet"


class NewDraftState(AbstractState):
    """
    Concrete state implementation.
    This class serves as start state for all users of "PelicanMarkdownBot".
    """

    def process_update(self, update):
        user_id = telegram.get_update_sender_id(update)
        chat_id = update["message"]["chat"]["id"]
        text = update["message"]["text"]

        if text == "/end":
            from packages.states.idlestate import IdleState
            self.get_context().set_user_state(user_id, IdleState(self.get_context()))
            self.get_context().send_message(chat_id, "Returning to IdleState")
        else:
            self.get_context().send_message(chat_id, "Enter /end.")