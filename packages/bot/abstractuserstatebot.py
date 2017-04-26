from packages.bot.abstracttelegrambot import AbstractTelegramBot

__author__ = "anaeanet"


class AbstractUserStateBot(AbstractTelegramBot):
    """
    Extending standard telegram bot functionality of receiving updates and sending messages.
    This bot class works like a finite state machine with multi-user support.
    """

    def __init__(self, token_url, start_state_class):
        super().__init__(token_url)
        self.__start_state_class = start_state_class
        self.__user_state_dict = dict()

        if type(self) is AbstractUserStateBot:
            raise TypeError("Abstract class! Cannot be instantiated.")

    def get_start_state_class(self):
        return self.__start_state_class

    def set_user_state(self, user_id, state):
        result = self.__user_state_dict[user_id] if user_id in self.__user_state_dict else None
        self.__user_state_dict[user_id] = state
        return result

    def get_user_state(self, user_id):
        return self.__user_state_dict[user_id] if user_id in self.__user_state_dict else None

    def handle_update(self, update):
        user_id = None

        for key in update:
            if key == "update_id":
                continue
            else:
                user_id = update[key]["from"]["id"]
                if user_id not in self.__user_state_dict or self.get_user_state(user_id) is None:
                    self.set_user_state(user_id, self.get_start_state_class()(self))

        self.get_user_state(user_id).process_update(update)