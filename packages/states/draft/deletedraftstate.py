from packages.states.navigation.idlestate import IdleState
from packages.datamodel.poststate import PostState

__author__ = "aneanet"


class DeleteDraftState(IdleState):
    """
    Concrete state implementation.

    Lets the user select a draft for deletion.
    """

    @property
    def welcome_message(self):
        return "Which <b>draft</b> do you want to <b>delete</b>?"

    @property
    def callback_options(self):
        reply_options = []

        # for all user drafts show corresponding button
        user_drafts = self.bot.persistence.get_posts(user_id=self.user_id, status=PostState.DRAFT)
        for post in user_drafts:
            button_text = post.title

            if post.original_post is not None:
                button_text = "[PUBLISHED] " + button_text

            reply_options.append({"text": button_text, "callback_data": "/deletedraft " + str(post.id)})

        # add button to return to main menu
        reply_options.append({"text": "<< main menu", "callback_data": "/mainmenu"})

        return reply_options

    def process_callback_query(self, user_id, chat_id, message_id, data):
        next_state = self
        command_array = data.split(" ")

        # only accept "/deletedraft <post_id>" callback queries
        if len(command_array) == 2 and command_array[0] == "/deletedraft":

            post_id = command_array[1]

            from packages.states.draft.confirmdraftdeletionstate import ConfirmDraftDeletionState
            next_state = ConfirmDraftDeletionState(self.bot, user_id, post_id, chat_id=chat_id, message_id=message_id)

        else:
            next_state = super().process_callback_query(user_id, chat_id, message_id, data)

        return next_state
