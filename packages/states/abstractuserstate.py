from packages.states.abstractstate import AbstractState
from packages.bot.keyboardtype import KeyboardType
from packages.bot.parsemode import ParseMode
import packages.bot.telegram as telegram

__author__ = "aneanet"


class AbstractUserState(AbstractState):
    """
    Abstract state class.
    Adds attributes user_id and message_id.
    Implements mandatory process_update and provides more specialized methods to process certain update types.
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
                                           , reply_markup=telegram.build_keyboard(reply_options
                                                                                  , KeyboardType.INLINE
                                                                                  , columns=keyboard_columns))
        else:
            sent_message = self.context.send_message(chat_id, message_text
                                                     , parse_mode=ParseMode.MARKDOWN.value
                                                     , reply_markup=telegram.build_keyboard(reply_options
                                                                                            , KeyboardType.INLINE
                                                                                            , columns=keyboard_columns))

            # store message_id of sent message to support later deletion or editing
            if "result" in sent_message and "message_id" in sent_message["result"]:
                if self.__message_id is None:
                    self.__message_id = sent_message["result"]["message_id"]
                else:
                    self.__message_id = max(sent_message["result"]["message_id"], self.__message_id)

    def process_message(self, user_id, chat_id, text):
        raise NotImplementedError("Abstract method! Implement in child class", type(self))

    def process_photo_message(self, user_id, chat_id, file_name, file_id, thumb_file_id=None, caption=None):
        raise NotImplementedError("Abstract method! Implement in child class", type(self))

    def process_callback_query(self, user_id, chat_id, message_id, data):
        raise NotImplementedError("Abstract method! Implement in child class", type(self))

    def process_update(self, update):
        update_type = telegram.get_update_type(update)

        if update_type == "message":
            user_id = telegram.get_update_sender_id(update)
            chat_id = update[update_type]["chat"]["id"]

            # check if user sent text message
            text = None
            if "text" in update[update_type]:
                text = update[update_type]["text"].strip(' \t\n\r')

            # check if user sent photo as a document (yes, if there is a thumbnail)
            document = None
            if "document" in update[update_type] and "thumb" in update[update_type]["document"]:
                document = update[update_type]["document"]

            # check if user sent photo message
            photo = None
            if "photo" in update[update_type]:
                photo = update[update_type]["photo"]

            # --- process specific message type ---

            # text message
            if text is not None:
                self.process_message(user_id, chat_id, text)

            # photo/document message
            elif document is not None or photo is not None:
                file_name = "IMG" + str(update[update_type]["message_id"])
                caption = update[update_type]["caption"] if "caption" in update[update_type] else None

                # picture was sent as document
                if document is not None:
                    file_id = document["file_id"]
                    thumb_id = document["thumb"]["file_id"] if "thumb" in document["thumb"] else None
                # picture was sent as photo
                else:
                    # sort photos by width
                    photo.sort(key=lambda x: x["width"])

                    file_id = photo[len(photo)-1]["file_id"]    # image with greatest size
                    thumb_id = photo[0]["file_id"]         # image with smallest size

                if file_id is not None and file_name is not None:
                    self.process_photo_message(user_id, chat_id, file_name, file_id, thumb_id=thumb_id, caption=caption)

        elif update_type == "callback_query":
            self.context.answer_callback_query(update[update_type]["id"])

            user_id = telegram.get_update_sender_id(update)
            chat_id = update[update_type]["message"]["chat"]["id"]
            message_id = update[update_type]["message"]["message_id"]
            data = update[update_type]["data"].strip(' \t\n\r') if "data" in update[update_type] else None

            self.process_callback_query(user_id, chat_id, message_id, data)

        else:   # unsupported update type
            print("unsupported update type:", update_type) # TODO change to log rather than print
