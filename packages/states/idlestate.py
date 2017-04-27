from packages.states.abstractstate import AbstractState
from packages.bot.parsemode import ParseMode
import packages.bot.telegram as telegram

__author__ = "aneanet"


class IdleState(AbstractState):
    """
    Concrete state implementation.
    This class serves as start state for all users of "PelicanMarkdownBot".
    """

    def process_update(self, update):
        print(update)

        user_id = telegram.get_update_sender_id(update)

        # TODO only process specific updates, i.e. message, edited_message, ...

        # TODO is user edits older message, there is no "message" key in update...
        if "message" not in update:
            return
        chat_id = update["message"]["chat"]["id"]

        # TODO sending foto with caption does not contain text
        if "text" not in update["message"]:
            return
        text = update["message"]["text"]

        if text == "/start":
            self.get_context().send_message(chat_id, "Welcome to your mobile blogging bot!"
                              + "\r\n" + "Send /help to see available commands.")
        elif text == "/help":
            self.get_context().send_message(chat_id, "*Drafts - Unpublished blog posts*"
                              + "\r\n" + "/createdraft - begin a new draft"
                              + "\r\n" + "/updatedraft - continue working on a draft"
                              + "\r\n" + "/deletedraft - delete a draft", parse_mode=ParseMode.MARKDOWN.value)
        elif text == "/createdraft":
            from packages.states.newdraftstate import NewDraftState
            self.get_context().set_user_state(user_id, NewDraftState(self.get_context()))
            self.get_context().send_message(chat_id, "What is the *title* of your new draft?", parse_mode=ParseMode.MARKDOWN.value)
        else:
            self.get_context().send_message(chat_id, text)

