import json

__author__ = "anaeanet"


def get_update_sender_id(update):
    result = None

    update_type = get_update_type(update)
    if "from" in update[update_type] and "id" in update[update_type]["from"]:
        result = update[update_type]["from"]["id"]

    return result


def get_update_type(update):
    result = None

    for item in update:
        if item == "update_id":
            continue
        else:
            result = item
            break

    return result


def build_keyboard(items, one_time_keyboard=True, resize_keyboard=True):
    if items is None:
        reply_markup = {"remove_keyboard": True}
    else:
        keyboard = [[item] for item in items]
        reply_markup = {"keyboard": keyboard, "one_time_keyboard": one_time_keyboard, "resize_keyboard": resize_keyboard}
    return json.dumps(reply_markup)


def build_inline_keyboard(items, columns=1):
    pos = 0
    keyboard = []

    while pos < len(items):
        keyboard_columns = [items[i] for i in list(range(pos, pos+columns))]
        pos += columns
        keyboard.append(keyboard_columns)

    return json.dumps({"inline_keyboard": keyboard})


def build_force_reply(selective=False):
    return json.dumps({"force_reply": True, "selective": selective})

