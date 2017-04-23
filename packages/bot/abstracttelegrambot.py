import json
import requests
import time
import urllib

import config

__author__ = "anaeanet"


def get_url_response(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url_response(url)
    js = json.loads(content)
    return js


def get_latest_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def build_keyboard(keyboard):
    reply_markup = {"keyboard": keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)


class AbstractTelegramBot:

    def __init__(self, database):
        self.__url = config.url.format(config.token)
        self.__database = database
        self.__next_update_id = None
        self.__user_state = dict()
        self.__start_state = None
        if type(self) is AbstractTelegramBot:
            raise TypeError("Abstract class! Cannot be instantiated.")

    def set_start_state(self, state):
        self.__start_state = state

    def set_user_state(self, user, state):
        self.__user_state[user] = state

    def get_updates(self, offset=None):
        url = self.__url + "getUpdates?timeout=100"
        if offset:
            url += "&offset={}".format(offset)
        js = get_json_from_url(url)
        return js

    def send_message(self, chat_id, content):
        url = self.__url + "sendMessage?chat_id={}".format(chat_id)
        for key in content:
            if key == "text":
                content[key] = urllib.parse.quote_plus(content[key])
            url += ("&" + key + "={}").format(content[key])
        get_url_response(url)

    def handle_update(self, update):
        user_id = None

        for key in update:
            if key == "update_id":
                continue
            else:
                user_id = update[key]["from"]["id"]
                if user_id not in self.__user_state:
                    self.set_user_state(user_id, self.__start_state)

        self.__user_state[user_id].process_update(update)

    def run(self):
        while True:
            updates = self.get_updates(self.__next_update_id)
            #updates["result"].sort(key=lambda x: x["update_id"])

            if len(updates["result"]) > 0:                                  #TODO obsolete after sorting updates
                self.__next_update_id = get_latest_update_id(updates) + 1   #TODO obsolete after sorting updates
                for update in updates["result"]:
                    self.handle_update(update)
                    #self.__next_update_id = max(self.__next_update_id, update["update_id"])
            time.sleep(0.5)
