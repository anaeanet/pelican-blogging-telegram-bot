import time

import config
import packages.bot.request_response as rr
from packages.bot.parsemode import ParseMode

__author__ = 'anaeanet'


class TelegramBot:

    def __init__(self, database):
        self.__DATABASE = database
        self.__lastupdateid = None

    def handle_updates(self, updates):
        for update in updates["result"]:
            text = update["message"]["text"]
            chatid = update["message"]["chat"]["id"]
            user = update["message"]["chat"]["username"]

            if text == "/start":
                rr.send_message(chatid, "Welcome to your mobile blogging bot!"
                                    + "\r\n" + "Send /help to see available commands.")
            elif text == "/help":
                rr.send_message(chatid, "*Drafts - Unpublished blog posts*"
                            + "\r\n" + "/createdraft - begin a new draft"
                            + "\r\n" + "/updatedraft - continue working on a draft"
                            + "\r\n" + "/deletedraft - delete a draft", parse_mode=ParseMode.MARKDOWN.value)
            elif text.startswith("/"):
                continue
            else:
                rr.send_message(chatid, text)

    def run(self):
        while True:
            updates = rr.get_updates(self.__lastupdateid)
            if len(updates["result"]) > 0:
                self.__lastupdateid = rr.get_last_update_id(updates) + 1
                self.handle_updates(updates)
            time.sleep(0.5)
