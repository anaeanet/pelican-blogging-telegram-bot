from packages.bot.parsemode import ParseMode
from packages.states.navigation.idlestate import IdleState
from packages.datamodel.poststate import PostState

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
        # add button to return to main menu
        return [{"text": "<< main menu", "callback_data": "/mainmenu"}]

    def process_message(self, user_id, chat_id, text, entities):
        next_state = self
        text = text.strip(' \t\n\r')

        # let super() handle any bot commands
        if text.startswith("/") or "bot_command" in [entity["type"] for entity in entities]:
            next_state = super().process_message(user_id, chat_id, text, entities)

        # accept simple text as post title
        else:
            # remove inline keyboard from latest bot message (by leaving out reply_options parameter)
            self.build_state_message(chat_id, self.welcome_message, message_id=self.message_id)

            # try to create new draft
            post = self.context.persistence.add_post(user_id, text, PostState.DRAFT, "Bildergalerie", "")

            # post creation was successful -> show post update options
            if post is not None:
                self.context.send_message(chat_id
                                            , "Draft <b>" + text + "</b> has been <b>created</b>."
                                            , parse_mode=ParseMode.HTML.value)
                from packages.states.navigation.selectdraftupdatestate import SelectDraftUpdateState
                next_state = SelectDraftUpdateState(self.context, user_id, post.id, chat_id=chat_id)

            # post creation failed -> back to main menu
            else:
                self.context.send_message(chat_id
                                          , "New draft could not be created. Returning to main menu."
                                          , parse_mode=ParseMode.HTML.value)
                next_state = IdleState(self.context, user_id, chat_id=chat_id)

        return next_state
