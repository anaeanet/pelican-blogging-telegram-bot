from packages.states.idlestate import IdleState
from packages.bot.parsemode import ParseMode

__author__ = "aneanet"


class CreateDraftState(IdleState):
    """
    Concrete state implementation.
    Accepts plain text message as draft title and creates new post.
    """

    @property
    def init_message(self):
        return "Enter the *title* of your *new draft*:"

    @property
    def initial_options(self):
        reply_options = [{"text": "<< main menu", "callback_data": "/mainmenu"}]
        return reply_options

    def process_message(self, user_id, chat_id, text):
        if text.startswith("/"):
            super().process_message(user_id, chat_id, text)
        else:
            # remove inline keyboard from latest bot message (by leaving out reply_options parameter)
            self.build_state_message(chat_id, self.init_message, message_id=self.message_id)

            self.context.add_post(user_id, text)
            self.context.send_message(chat_id
                                            , "Successfully created draft *" + text + "*"
                                            , parse_mode=ParseMode.MARKDOWN.value)
            next_state = IdleState(self.context, user_id, chat_id=chat_id)
            self.context.set_user_state(user_id, next_state)
