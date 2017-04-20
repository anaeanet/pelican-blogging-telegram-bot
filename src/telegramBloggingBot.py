__author__ = 'anaeanet'

import json
import requests
import time
import urllib

import config
from dbwrapper import DBWrapper
from parsemode import ParseMode

TOKEN = config.token
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
USERS = config.users

db = DBWrapper()


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
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


def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)


def send_message(chat_id, text, reply_markup=None, parse_mode=None):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    if parse_mode:
        url += "&parse_mode={}".format(parse_mode)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)


def handle_updates(updates):
    for update in updates["result"]:
        text = update["message"]["text"]
        chat = update["message"]["chat"]["id"]
        user = update["message"]["chat"]["username"]
        posts = db.get_posts(user)

        if user not in USERS:
            None
            # TODO: log message in db, username, first/last name, message timestamp, chat id
        elif text == "/start":
            send_message(chat, "Welcome to your mobile blogging bot!"
                                + "\r\n" + "Send /help to see available commands.")
        elif text == "/help":
            send_message(chat, "*Drafts - Unpublished blog posts*"
                        + "\r\n" + "/createdraft - begin a new draft"
                        + "\r\n" + "/updatedraft - continue working on a draft"
                        + "\r\n" + "/deletedraft - delete a draft", parse_mode=ParseMode.MARKDOWN.value)
        elif text.startswith("/"):
            continue
        else:
            None


def main():
    db.setup()
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            handle_updates(updates)
        time.sleep(0.5)


if __name__ == '__main__':
    main()