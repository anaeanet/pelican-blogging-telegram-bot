import packages.bot.telegram as telegram
import logging
from packages.bot.keyboardtype import KeyboardType
from packages.bot.parsemode import ParseMode
from packages.states.abstract.abstractstate import AbstractState

__author__ = "aneanet"


class AbstractUserState(AbstractState):
    """
    Abstract state class.
    Adds attributes user_id and message_id.
    Implements mandatory process_update and provides more specialized methods to process certain update types.
    """

    def __init__(self, bot, user_id, chat_id=None, message_id=None):
        self.__user_id = user_id
        self.__message_id = message_id
        super().__init__(bot)

        if chat_id is not None:
            self.build_state_message(chat_id, self.welcome_message, message_id=message_id, reply_options=self.callback_options)

        if type(self) is AbstractUserState:
            raise TypeError("Abstract class! Cannot be instantiated.")

    @property
    def user_id(self):
        return self.__user_id

    @property
    def message_id(self):
        return self.__message_id

    @property
    def welcome_message(self):
        raise NotImplementedError("Abstract method! Implement in child class", type(self))

    @property
    def callback_options(self):
        raise NotImplementedError("Abstract method! Implement in child class", type(self))

    def build_state_message(self, chat_id, message_text, message_id=None, reply_options=None, keyboard_columns=1):
        logger = logging.getLogger("pelicanBlogBot.packages.states.abstractuserstate.build_state_message")

        if message_id is not None:
            self.bot.edit_message_text(chat_id, message_id, message_text
                                       , parse_mode=ParseMode.HTML.value
                                       , reply_markup=telegram.build_keyboard(reply_options
                                                                                  , KeyboardType.INLINE
                                                                                  , columns=keyboard_columns))
        else:
            sent_message = self.bot.send_message(chat_id, message_text
                                                 , parse_mode=ParseMode.HTML.value
                                                 , reply_markup=telegram.build_keyboard(reply_options
                                                                                            , KeyboardType.INLINE
                                                                                            , columns=keyboard_columns))

            # store message_id of sent message to support later deletion or editing
            if "result" in sent_message and "message_id" in sent_message["result"]:
                if self.__message_id is None:
                    self.__message_id = sent_message["result"]["message_id"]
                else:
                    self.__message_id = max(sent_message["result"]["message_id"], self.__message_id)
            else:
                logger.warning("sending message '" + message_text + "' to user " + str(chat_id) + " failed.")

    def process_message(self, user_id, chat_id, text, entities):
        raise NotImplementedError("Abstract method! Implement in child class", type(self))

    def process_photo_message(self, user_id, chat_id, file_id, thumb_file_id=None, caption=None):
        raise NotImplementedError("Abstract method! Implement in child class", type(self))

    def process_callback_query(self, user_id, chat_id, message_id, data):
        raise NotImplementedError("Abstract method! Implement in child class", type(self))

    def process_unknown_update(self, chat_id):

        # delete previous bot message (if existing) before sending new ones
        if self.message_id is not None:
            result = self.bot.delete_message(chat_id, self.message_id)
            # edit message instead if deletion does not work due to message being too old
            if False in result.values():
                self.bot.edit_message_text(chat_id, self.message_id, "Message/Command not recognized!")

        # simply ignore arbitrary update by moving current bot message underneath latest user message
        self.build_state_message(chat_id, self.welcome_message, reply_options=self.callback_options)

        return self

    def process_update(self, update):
        logger = logging.getLogger("pelicanBlogBot.packages.states.abstractuserstate.process_update")

        next_state = self
        update_type = telegram.get_update_type(update)
        user_id = telegram.get_update_sender_id(update)

        if update_type == "message":
            chat_id = update[update_type]["chat"]["id"]

            # check if user sent text message
            text = None
            if "text" in update[update_type]:
                text = update[update_type]["text"].strip(' \t\n\r')
                entities = update[update_type]["entities"] if "entities" in update[update_type] else []

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
                next_state = self.process_message(user_id, chat_id, text, entities)

            # photo/document message
            elif document or photo:
                caption = update[update_type]["caption"] if "caption" in update[update_type] else None

                # picture was sent as document
                if document:
                    file_id = document["file_id"]
                    thumb_id = document["thumb"]["file_id"] if "thumb" in document else None

                # picture was sent as photo
                else:
                    # sort photos by width
                    photo.sort(key=lambda x: x["width"])

                    file_id = photo[len(photo)-1]["file_id"]    # image with greatest size
                    thumb_id = photo[0]["file_id"]              # image with smallest size

                if file_id is not None:
                    next_state = self.process_photo_message(user_id, chat_id, file_id, thumb_id=thumb_id, caption=caption)

            else:
                next_state = self.process_unknown_update(chat_id)

        elif update_type == "callback_query":
            self.bot.answer_callback_query(update[update_type]["id"])

            chat_id = update[update_type]["message"]["chat"]["id"]
            message_id = update[update_type]["message"]["message_id"]
            data = update[update_type]["data"].strip(' \t\n\r') if "data" in update[update_type] else None

            if data is not None:
                next_state = self.process_callback_query(user_id, chat_id, message_id, data)
            else:
                next_state = self.process_unknown_update(chat_id)

        else:   # unsupported update type
            logger.info("user " + str(user_id) + " sent unsupported update '" + update_type + "': " + str(update[update_type]))

        return next_state
