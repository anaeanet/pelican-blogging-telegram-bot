from packages.bot.keyboardtype import KeyboardType
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


def build_keyboard(items, keyboard_type, columns=1, one_time_keyboard=False, resize_keyboard=False):
    result = None

    keyboard = []
    item_pos = 0
    while items is not None and item_pos < len(items):
        keyboard_columns = []
        for i in list(range(item_pos, min(item_pos+columns, len(items)))):
            item = items[i]
            if item:    # empty/None item indicates a line break
                keyboard_columns.append(items[i])
        keyboard.append(keyboard_columns)
        item_pos += columns

    if keyboard_type == KeyboardType.INLINE:
        result = json.dumps({keyboard_type.value: keyboard})

    elif keyboard_type == KeyboardType.KEYBOARD:
        result = json.dumps({keyboard_type.value: keyboard
                                , "one_time_keyboard": one_time_keyboard
                                , "resize_keyboard": resize_keyboard})

    return result


