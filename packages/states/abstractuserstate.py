from packages.states.abstractstate import AbstractState
from packages.bot.parsemode import ParseMode
import packages.bot.telegram as telegram

__author__ = "aneanet"


class AbstractUserState(AbstractState):
    """
    Abstract state class.
    Adds attributes user_id and message_id.
    Implements mandatory process_update and provides more specialized methods to proces certain update types.
    """

    def __init__(self, context, user_id, chat_id=None, message_id=None):
        self.__user_id = user_id
        self.__message_id = message_id
        super().__init__(context)

        if chat_id is not None:
            self.build_state_message(chat_id, self.init_message, message_id=message_id, reply_options=self.initial_options)

        if type(self) is AbstractUserState:
            raise TypeError("Abstract class! Cannot be instantiated.")

    @property
    def user_id(self):
        return self.__user_id

    @property
    def message_id(self):
        return self.__message_id

    # TODO remove if not used by any child class
    @message_id.setter
    def message_id(self, message_id):
        self.__message_id = message_id if self.__message_id is None or message_id > self.__message_id else self.__message_id

    @property
    def init_message(self):
        raise NotImplementedError("Abstract method! Implement in child class", type(self))

    @property
    def initial_options(self):
        raise NotImplementedError("Abstract method! Implement in child class", type(self))

    def build_state_message(self, chat_id, message_text, message_id=None, reply_options=None, keyboard_columns=1):
        if message_id is not None:
            self.context.edit_message_text(chat_id, message_id, message_text
                                            , parse_mode=ParseMode.MARKDOWN.value
                                            , reply_markup=telegram.build_inline_keyboard(reply_options, keyboard_columns))
        else:
            sent_message = self.context.send_message(chat_id, message_text
                                            , parse_mode=ParseMode.MARKDOWN.value
                                            , reply_markup=telegram.build_inline_keyboard(reply_options, keyboard_columns))

            # store message_id of sent message to support later deletion or editing
            if "result" in sent_message and "message_id" in sent_message["result"]:
                self.message_id = sent_message["result"]["message_id"]

    def process_message(self, user_id, chat_id, text):
        raise NotImplementedError("Abstract method! Implement in child class", type(self))

    def process_callback_query(self, user_id, chat_id, message_id, data):
        raise NotImplementedError("Abstract method! Implement in child class", type(self))

    def process_update(self, update):
        update_type = telegram.get_update_type(update)

        if update_type == "message":
            user_id = telegram.get_update_sender_id(update)
            chat_id = update[update_type]["chat"]["id"]
            text = update[update_type]["text"].strip(' \t\n\r') if "text" in update[update_type] else None

            # TODO treat non-text messages differently, i.e. photo or document

            self.process_message(user_id, chat_id, text)

        elif update_type == "callback_query":
            self.context.answer_callback_query(update[update_type]["id"])

            user_id = telegram.get_update_sender_id(update)
            chat_id = update[update_type]["message"]["chat"]["id"]
            message_id = update[update_type]["message"]["message_id"]
            data = update[update_type]["data"].strip(' \t\n\r') if "data" in update[update_type] else None

            self.process_callback_query(user_id, chat_id, message_id, data)

        else:   # unsupported update type
            print("unsupported update type:", update_type) # TODO change to log rather than print
