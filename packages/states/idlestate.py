from packages.states.abstractstate import AbstractState
from packages.bot.parsemode import ParseMode
import packages.bot.telegram as telegram

__author__ = "aneanet"


class IdleState(AbstractState):
    """
    Concrete state implementation.
    This class serves as start state for all users of "PelicanMarkdownBot".
    """

    def get_global_commands(self):
        # TODO add /previewdraft and /publishdraft
        return ["/start", "/help", "/createdraft", "/updatedraft", "/deletedraft"]

    def notify_invalid_command(self, chat_id):
        self.get_context().send_message(chat_id, "Unrecognized command or message!"
                                        + "\r\n" + "Send /help to see available commands."
                                        , parse_mode=ParseMode.MARKDOWN.value)

    def process_message(self, user_id, chat_id, text):
        # global commands
        if text in ["/start", "/help"]:
            self.get_context().send_message(chat_id,
                                            "Welcome to your mobile blogging bot! I am here to help you create new blog posts or update existing ones while you are on the go."
                                            + "\r\n"
                                            + "\r\n" + "You can control me by the following commands:"
                                            + "\r\n"
                                            + "\r\n" + "*Drafts - Unpublished blog posts*"
                                            + "\r\n" + "/createdraft - begin a new draft"
                                            + "\r\n" + "/updatedraft - continue working on a draft"
                                            + "\r\n" + "/deletedraft - delete a draft"
                                            , parse_mode=ParseMode.MARKDOWN.value)
            self.get_context().set_user_state(user_id, IdleState(self.get_context()))
        elif text == "/createdraft":
            from packages.states.createdraftstate import CreateDraftState
            self.get_context().set_user_state(user_id, CreateDraftState(self.get_context(), chat_id=chat_id))
        elif text == "/updatedraft":
            from packages.states.updatedraft import UpdateDraftState
            self.get_context().set_user_state(user_id, UpdateDraftState(self.get_context(), chat_id=chat_id, user_id=user_id))
        elif text == "/deletedraft":
            from packages.states.deletedraftstate import DeleteDraftState
            self.get_context().set_user_state(user_id, DeleteDraftState(self.get_context(), chat_id=chat_id, user_id=user_id))

        # unsupported command(s)
        else:
            self.notify_invalid_command(chat_id)

    def process_update(self, update):
        update_type = telegram.get_update_type(update)

        if update_type == "message":
            user_id = telegram.get_update_sender_id(update)
            chat_id = update[update_type]["chat"]["id"]
            text = update[update_type]["text"].strip(' \t\n\r') if "text" in update[update_type] else None

            if text:
                self.process_message(user_id, chat_id, text)
            else:
                self.notify_invalid_command(chat_id)

        else:   # unsupported update type
            print("unsupported update type:", update_type) # TODO change to log rather than print
