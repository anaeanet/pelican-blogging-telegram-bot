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
        update_type = telegram.get_update_type(update)

        if update_type == "message":
            chat_id = update["message"]["chat"]["id"]
            text =  update[update_type]["text"].strip(' \t\n\r') if "text" in update[update_type] else None

            if text:
                # text message

                if text == "/start":
                    self.get_context().send_message(chat_id, "Welcome to your mobile blogging bot!"
                                      + "\r\n" + "Send /help to see currently available commands.")
                    # TODO send custom reply keyboard with available commands to chose from
                    return

                elif text == "/help":
                    self.get_context().send_message(chat_id, "*Drafts - Unpublished blog posts*"
                                      + "\r\n" + "/createdraft - begin a new draft"
                                      + "\r\n" + "/updatedraft - continue working on a draft"
                                      + "\r\n" + "/deletedraft - delete a draft", parse_mode=ParseMode.MARKDOWN.value)
                    return

                elif text == "/createdraft":
                    from packages.states.newdraftstate import NewDraftState
                    self.get_context().send_message(chat_id, "What is the draft's *title*?", parse_mode=ParseMode.MARKDOWN.value)
                    self.get_context().set_user_state(user_id, NewDraftState(self.get_context()))
                    # TODO send custom reply keyboard with available commands to chose from
                    return

        self.get_context().send_message(chat_id, "Unrecognized command or message!"
                                        + "\r\n" + "Send /help to see currently available commands.")
