from packages.bot.parsemode import ParseMode
from packages.states.navigation.idlestate import IdleState

__author__ = "aneanet"


class CreateDraftState(IdleState):
    """
    Concrete state implementation.
    Accepts plain text message as draft title and creates new post.
    """

    @property
    def welcome_message(self):
        return "Enter your new <b>draft's title</b>:"

    @property
    def callback_options(self):
        reply_options = [{"text": "<< main menu", "callback_data": "/mainmenu"}]
        return reply_options

    def process_message(self, user_id, chat_id, text, entities):
        next_state = self

        if text.startswith("/"):
            next_state = super().process_message(user_id, chat_id, text)
        else:
            # remove inline keyboard from latest bot message (by leaving out reply_options parameter)
            self.build_state_message(chat_id, self.welcome_message, message_id=self.message_id)

            post_id = self.context.add_post(user_id, text)

            # post creation was successful -> show post update options
            if post_id:
                self.context.send_message(chat_id
                                            , "Draft <b>" + text + "</b> has been <b>created</b>."
                                            , parse_mode=ParseMode.HTML.value)
                from packages.states.navigation.selectdraftupdatestate import SelectDraftUpdateState
                next_state = SelectDraftUpdateState(self.context, user_id, post_id, chat_id=chat_id)

            # post creation failed -> back to main menu
            else:
                self.context.send_message(chat_id
                                          , "New draft could not be created. Returning to main menu."
                                          , parse_mode=ParseMode.HTML.value)
                next_state = IdleState(self.context, user_id, chat_id=chat_id)

        return next_state
