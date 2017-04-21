from packages.bot.telegrambot import *
from packages.bot.parsemode import ParseMode

__author__ = "anaeanet"


class PelicanBot(TelegramBot):

    def handle_updates(self, updates):
        for update in updates["result"]:
            text = update["message"]["text"]
            chatid = update["message"]["chat"]["id"]
            user = update["message"]["chat"]["username"]
            posts = self.__DATABASE.get_posts(user)

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
