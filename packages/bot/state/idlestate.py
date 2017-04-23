from packages.bot.state.abstractstate import AbstractState
from packages.bot.parsemode import ParseMode

__author__ = "aneanet"


class IdleState(AbstractState):

    def __init__(self, context):
        self.__context = context

    def process_update(self, update):
        print(update)

        # TODO is user edits older message, there is no "message" key in update...
        if "message" not in update:
            return
        user = update["message"]["chat"]["username"]
        chat_id = update["message"]["chat"]["id"]

        # TODO sending foto with caption does not contain text
        if "text" not in update["message"]:
            return
        text = update["message"]["text"]

        # TODO only react if user is authorized to interact with bot

        if text == "/start":
            self.__context.send_message(chat_id, {"text":"Welcome to your mobile blogging bot!"
                              + "\r\n" + "Send /help to see available commands."})
        elif text == "/help":
            self.__context.send_message(chat_id, {"text":"*Drafts - Unpublished blog posts*"
                              + "\r\n" + "/createdraft - begin a new draft"
                              + "\r\n" + "/updatedraft - continue working on a draft"
                              + "\r\n" + "/deletedraft - delete a draft", "parse_mode":ParseMode.MARKDOWN.value})
        elif text.startswith("/"):
            None
        else:
            self.__context.send_message(chat_id, {"text":text})