import json
import requests
import time
import urllib

import config
from packages.bot.parsemode import ParseMode

__author__ = "anaeanet"


class TelegramBot:

    def __init__(self, database):
        self.__url = config.url.format(config.token)
        self.__DATABASE = database
        self.__lastupdateid = None

    def get_url_response(self, url):
        response = requests.get(url)
        content = response.content.decode("utf8")
        return content

    def get_json_from_url(self, url):
        content = self.get_url_response(url)
        js = json.loads(content)
        return js

    def get_updates(self, offset=None):
        url = self.__url + "getUpdates?timeout=100"
        if offset:
            url += "&offset={}".format(offset)
        js = self.get_json_from_url(url)
        return js

    def get_last_update_id(self, updates):
        update_ids = []
        for update in updates["result"]:
            update_ids.append(int(update["update_id"]))
        return max(update_ids)

    def build_keyboard(self, keyboard):
        reply_markup = {"keyboard": keyboard, "one_time_keyboard": True}
        return json.dumps(reply_markup)

    def send_message(self, chat_id, text, reply_markup=None, parse_mode=None):
        text = urllib.parse.quote_plus(text)
        url = self.__url + "sendMessage?text={}&chat_id={}".format(text, chat_id)
        if parse_mode:
            url += "&parse_mode={}".format(parse_mode)
        if reply_markup:
            url += "&reply_markup={}".format(reply_markup)
        self.get_url_response(url)

    def handle_updates(self, updates):
        for update in updates["result"]:
            text = update["message"]["text"]
            chatid = update["message"]["chat"]["id"]
            user = update["message"]["chat"]["username"]

            if text == "/start":
                self.send_message(chatid, "Welcome to your mobile blogging bot!"
                                    + "\r\n" + "Send /help to see available commands.")
            elif text == "/help":
                self.send_message(chatid, "*Drafts - Unpublished blog posts*"
                            + "\r\n" + "/createdraft - begin a new draft"
                            + "\r\n" + "/updatedraft - continue working on a draft"
                            + "\r\n" + "/deletedraft - delete a draft", parse_mode=ParseMode.MARKDOWN.value)
            elif text.startswith("/"):
                continue
            else:
                self.send_message(chatid, text)

    def run(self):
        while True:
            updates = self.get_updates(self.__lastupdateid)
            if len(updates["result"]) > 0:
                self.__lastupdateid = self.get_last_update_id(updates) + 1
                self.handle_updates(updates)
            time.sleep(0.5)
