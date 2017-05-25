from packages.states.abstractuserstate import AbstractUserState

__author__ = "aneanet"


class AbstractUserPostState(AbstractUserState):
    """
    Abstract state class.
    Adds attribute post_id.
    """

    def __init__(self, context, user_id, post_id, chat_id=None, message_id=None):
        self.__post_id = post_id
        super().__init__(context, user_id, chat_id=chat_id, message_id=message_id)

    @property
    def post_id(self):
        return self.__post_id

    def build_state_message(self, chat_id, message_text, message_id=None, reply_options=None, keyboard_columns=2):
        super().build_state_message(chat_id, message_text, message_id=message_id, reply_options=reply_options, keyboard_columns=keyboard_columns)
