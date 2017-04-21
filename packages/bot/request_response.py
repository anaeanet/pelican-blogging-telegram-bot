import json
import requests
import urllib

import config

__author__ = "anaeanet"

TOKEN = config.token
URL = config.url.format(TOKEN)


def get_url_response(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url_response(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def build_keyboard(self, keyboard):
    reply_markup = {"keyboard":keyboard, "one_time_keyboard":True}
    return json.dumps(reply_markup)


def send_message(chat_id, text, reply_markup=None, parse_mode=None):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    if parse_mode:
        url += "&parse_mode={}".format(parse_mode)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url_response(url)
