from packages.states.abstractstate import AbstractState
from packages.bot.parsemode import ParseMode

__author__ = "aneanet"


class IdleState(AbstractState):
    """
    Concrete state implementation.
    This class serves as start state for all users of "PelicanMarkdownBot".
    """

    def process_update(self, update):
        print(update)

        # TODO only process specific updates, i.e. message, edited_message, ...

        # TODO is user edits older message, there is no "message" key in update...
        if "message" not in update:
            return
        user_id = update["message"]["from"]["id"]
        chat_id = update["message"]["chat"]["id"]

        # TODO sending foto with caption does not contain text
        if "text" not in update["message"]:
            return
        text = update["message"]["text"]

        # TODO only react if user is authorized to interact with bot

        if text == "/start":
            self.get_context().send_message(chat_id, "Welcome to your mobile blogging bot!"
                              + "\r\n" + "Send /help to see available commands.")
        elif text == "/help":
            self.get_context().send_message(chat_id, "*Drafts - Unpublished blog posts*"
                              + "\r\n" + "/createdraft - begin a new draft"
                              + "\r\n" + "/updatedraft - continue working on a draft"
                              + "\r\n" + "/deletedraft - delete a draft", parse_mode=ParseMode.MARKDOWN.value)
        elif text.startswith("/"):
            None
        else:
            self.get_context().send_message(chat_id, text)

        #TODO update user status after processing message
        #self.__context.set_user_state(user_id, <targetState>)