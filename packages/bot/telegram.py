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
