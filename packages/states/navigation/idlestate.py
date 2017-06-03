from packages.bot.parsemode import ParseMode
from packages.states.abstract.abstractuserstate import AbstractUserState

__author__ = "aneanet"


class IdleState(AbstractUserState):
    """
    Concrete state implementation.
    This class serves as start state for all users of "PelicanMarkdownBot" 
    and provides functionality to process common commands and navigation.
    """

    @property
    def welcome_message(self):
        return "What do you want to do?"

    @property
    def callback_options(self):
        reply_options = [{"text": "CREATE a draft", "callback_data": "/createdraft"}]
        user_drafts = self.context.get_posts(user_id=self.user_id, status="draft")
        if len(user_drafts) > 0:
            reply_options.append({"text": "UPDATE a draft", "callback_data": "/updatedraft"})
            reply_options.append({"text": "DELETE a draft", "callback_data": "/deletedraft"})
            # TODO
            # reply_options.append({"text": "PREVIEW a draft", "callback_data": "/previewdraft"})
            # reply_options.append({"text": "PUBLISH a draft", "callback_data": "/publishdraft"})
        return reply_options

    def process_message(self, user_id, chat_id, text, entities):

        # delete previous bot message (if existing) before sending new ones
        if self.message_id is not None:
            self.context.delete_message(chat_id, self.message_id)

        # welcome message
        if text in ["/start"]:
            self.context.send_message(chat_id,
                                            "Welcome to your mobile blogging bot!"
                                            + "\r\n"
                                            + "\r\n"
                                            + "I am here to help you create new blog posts or manage existing ones. "
                                            + "Just follow the interactive menu!"
                                            , parse_mode=ParseMode.HTML.value)
            # reset to start state
            next_state = IdleState(self.context, user_id, chat_id=chat_id)
            self.context.set_state(user_id, next_state)

        # simply ignore arbitrary text message by moving current bot message underneath latest user message
        else:
            self.build_state_message(chat_id, self.welcome_message, reply_options=self.callback_options)

    def process_photo_message(self, user_id, chat_id, file_name, file_id, thumb_id=None, caption=None):

        # delete previous bot message (if existing) before sending new ones
        if self.message_id is not None:
            self.context.delete_message(chat_id, self.message_id)

        # simply ignore arbitrary photo message by moving current bot message underneath latest user message
        self.build_state_message(chat_id, self.welcome_message, reply_options=self.callback_options)

    def process_callback_query(self, user_id, chat_id, message_id, data):
        command_array = data.split(" ")

        if len(command_array) > 0:

            if command_array[0] == "/mainmenu":
                next_state = IdleState(self.context, user_id, chat_id=chat_id, message_id=message_id)
                self.context.set_state(user_id, next_state)
            elif command_array[0] == "/createdraft":
                from packages.states.draft.createdraftstate import CreateDraftState
                next_state = CreateDraftState(self.context, user_id, chat_id=chat_id, message_id=message_id)
                self.context.set_state(user_id, next_state)
            elif command_array[0] == "/updatedraft":
                from packages.states.draft.updatedraftstate import UpdateDraftState
                next_state = UpdateDraftState(self.context, user_id, chat_id=chat_id, message_id=message_id)
                self.context.set_state(user_id, next_state)
            elif command_array[0] == "/deletedraft":
                from packages.states.draft.deletedraftstate import DeleteDraftState
                next_state = DeleteDraftState(self.context, user_id, chat_id=chat_id, message_id=message_id)
                self.context.set_state(user_id, next_state)
            elif command_array[0] == "/previewdraft":
                # TODO
                None
            elif command_array[0] == "/publishdraft":
                # TODO
                None
