import json
import requests
import urllib

__author__ = "anaeanet"


class AbstractTelegramBot:
    """
    Very basic abstract telegram bot class.
    It only takes care of receiving updates and sending messages.
    """

    def __init__(self, token_url):
        self.__url = token_url
        self.__next_update_id = None

        if type(self) is AbstractTelegramBot:
            raise TypeError("Abstract class! Cannot be instantiated.")

    def __get_url_response(url):
        response = requests.get(url)
        content = response.content.decode("utf8")
        return content

    def __get_json_from_url(url):
        content = AbstractTelegramBot.__get_url_response(url)
        js = json.loads(content)
        return js

    def get_updates(self, allowed_updates=[], limit=None, offset=None, timeout=None):
        url = self.__url + "getUpdates?allowed_updates={}".format(allowed_updates)

        if limit is not None:
            url += "&limit={}".format(limit)
        if offset is not None:
            url += "&offset={}".format(offset)
        if timeout is not None:
            url += "&timeout={}".format(timeout)

        js = AbstractTelegramBot.__get_json_from_url(url)
        return js

    def send_message(self, chat_id, text, disable_web_page_preview=None, disable_notification=None, parse_mode=None, reply_to_message_id=None, reply_markup=None):
        url = self.__url + "sendMessage?chat_id={}&text={}".format(chat_id, urllib.parse.quote_plus(text))

        if disable_web_page_preview is not None:
            url += "&disable_web_page_preview={}".format(disable_web_page_preview)
        if disable_notification is not None:
            url += "&disable_notification={}".format(disable_notification)
        if parse_mode is not None:
            url += "&parse_mode={}".format(parse_mode)
        if reply_to_message_id is not None:
            url += "&reply_to_message_id={}".format(reply_to_message_id)
        if reply_markup is not None:
            url += "&reply_markup={}".format(reply_markup)

        AbstractTelegramBot.__get_url_response(url)

    def handle_update(self, update):
        raise NotImplementedError("Abstract method! Implement in child class", type(self))

    def run(self):
        while True:
            updates = self.get_updates(offset=self.__next_update_id)
            updates["result"].sort(key=lambda x: x["update_id"])

            for update in updates["result"]:
                self.handle_update(update)
                self.__next_update_id = update["update_id"] + 1
