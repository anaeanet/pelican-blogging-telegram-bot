from packages.states.abstractuserstate import AbstractUserState
from packages.bot.parsemode import ParseMode

__author__ = "aneanet"


class IdleState(AbstractUserState):
    """
    Concrete state implementation.
    This class serves as start state for all users of "PelicanMarkdownBot".
    """

    @property
    def init_message(self):
        return "What do you want to do?"

    @property
    def initial_options(self):
        reply_options = [{"text": "CREATE a draft", "callback_data": "/createdraft"}]
        if len(self.context.get_posts(user_id=self.user_id, status="draft")) > 0:
            reply_options.append({"text": "UPDATE a draft", "callback_data": "/updatedraft"})
            reply_options.append({"text": "DELETE a draft", "callback_data": "/deletedraft"})
            # TODO
            # reply_options.append({"text": "PREVIEW a draft", "callback_data": "/previewdraft"})
            # reply_options.append({"text": "PUBLISH a draft", "callback_data": "/publishdraft"})
        return reply_options

    def process_message(self, user_id, chat_id, text):

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
                                            , parse_mode=ParseMode.MARKDOWN.value)

        # TODO maybe arbitrary text message shouldn't return to IdleState, but preserve current state?
        """ 
            next_state = IdleState(self.context, user_id, chat_id=chat_id)
            self.context.set_user_state(user_id, next_state)
        else:
            self.build_state_message(chat_id, self.init_message, reply_options=self.initial_options)
        """

        # arbitrary text message sets status back to IdleState
        next_state = IdleState(self.context, user_id, chat_id=chat_id)
        self.context.set_user_state(user_id, next_state)

    def process_callback_query(self, user_id, chat_id, message_id, data):
        command_array = data.split(" ")

        if len(command_array) > 0:

            if command_array[0] == "/mainmenu":
                next_state = IdleState(self.context, user_id, chat_id=chat_id, message_id=message_id)
                self.context.set_user_state(user_id, next_state)
            elif command_array[0] == "/createdraft":
                from packages.states.createdraftstate import CreateDraftState
                next_state = CreateDraftState(self.context, user_id, chat_id=chat_id, message_id=message_id)
                self.context.set_user_state(user_id, next_state)
            elif command_array[0] == "/updatedraft":
                from packages.states.updatedraft import UpdateDraftState
                next_state = UpdateDraftState(self.context, user_id, chat_id=chat_id, message_id=message_id)
                self.context.set_user_state(user_id, next_state)
            elif command_array[0] == "/deletedraft":
                from packages.states.deletedraftstate import DeleteDraftState
                next_state = DeleteDraftState(self.context, user_id, chat_id=chat_id, message_id=message_id)
                self.context.set_user_state(user_id, next_state)
            elif command_array[0] == "/previewdraft":
                # TODO
                None
            elif command_array[0] == "/publishdraft":
                # TODO
                None
