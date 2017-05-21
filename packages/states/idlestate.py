from packages.states.abstractstate import AbstractState
from packages.bot.parsemode import ParseMode
import packages.bot.telegram as telegram

__author__ = "aneanet"


class IdleState(AbstractState):
    """
    Concrete state implementation.
    This class serves as start state for all users of "PelicanMarkdownBot".
    """

    def __init__(self, context, user_id, chat_id=None, message_id=None):
        super().__init__(context)

        if chat_id is not None:
            self.show_menu(user_id, chat_id, message_id=message_id)

    def show_menu(self, user_id, chat_id, message_id=None):
        reply_options = [{"text": "CREATE a draft", "callback_data": "/createdraft"}]
        if len(self.get_context().get_posts(user_id=user_id, status="draft")) > 0:
            reply_options.append({"text": "UPDATE a draft", "callback_data": "/updatedraft"})
            reply_options.append({"text": "DELETE a draft", "callback_data": "/deletedraft"})
            # TODO
            #reply_options.append({"text": "PREVIEW a draft", "callback_data": "/previewdraft"})
            #reply_options.append({"text": "PUBLISH a draft", "callback_data": "/publishdraft"})

        message_text = "What do you want to do?"
        if message_id is not None:
            self.get_context().edit_message_text(chat_id, message_id, message_text
                                            , parse_mode=ParseMode.MARKDOWN.value
                                            , reply_markup=telegram.build_inline_keyboard(reply_options))
        else:
            self.get_context().send_message(chat_id, message_text
                                            , parse_mode=ParseMode.MARKDOWN.value
                                            , reply_markup=telegram.build_inline_keyboard(reply_options))

    def process_message(self, user_id, chat_id, text):

        if text in ["/start", "/help"]:
            self.get_context().send_message(chat_id,
                                            "Welcome to your mobile blogging bot!"
                                            + "\r\n"
                                            + "\r\n"
                                            + "I am here to help you create new blog posts or manage existing ones. "
                                            + "Just follow the interactive menu!"
                                            , parse_mode=ParseMode.MARKDOWN.value)

        self.show_menu(user_id, chat_id)
        self.get_context().set_user_state(user_id, IdleState(self.get_context(), user_id))

    def process_callback_query(self, user_id, chat_id, message_id, data):
        if data == "/createdraft":
            from packages.states.createdraftstate import CreateDraftState
            self.get_context().set_user_state(user_id,
                                              CreateDraftState(self.get_context(), user_id, chat_id=chat_id, message_id=message_id))
        elif data == "/updatedraft":
            from packages.states.updatedraft import UpdateDraftState
            self.get_context().set_user_state(user_id,
                                              UpdateDraftState(self.get_context(), user_id, chat_id=chat_id, message_id=message_id))
        elif data == "/deletedraft":
            from packages.states.deletedraftstate import DeleteDraftState
            self.get_context().set_user_state(user_id,
                                              DeleteDraftState(self.get_context(), user_id, chat_id=chat_id, message_id=message_id))
        elif data == "/previewdraft":
            # TODO
            None
        elif data == "/publishdraft":
            # TODO
            None

    def process_update(self, update):
        update_type = telegram.get_update_type(update)

        if update_type == "message":
            user_id = telegram.get_update_sender_id(update)
            chat_id = update[update_type]["chat"]["id"]
            text = update[update_type]["text"].strip(' \t\n\r') if "text" in update[update_type] else None

            self.process_message(user_id, chat_id, text)

        elif update_type == "callback_query":
            self.get_context().answer_callback_query(update[update_type]["id"])

            user_id = telegram.get_update_sender_id(update)
            chat_id = update[update_type]["message"]["chat"]["id"]
            message_id = update[update_type]["message"]["message_id"]
            data = update[update_type]["data"].strip(' \t\n\r') if "data" in update[update_type] else None

            self.process_callback_query(user_id, chat_id, message_id, data)

        else:   # unsupported update type
            print("unsupported update type:", update_type) # TODO change to log rather than print
