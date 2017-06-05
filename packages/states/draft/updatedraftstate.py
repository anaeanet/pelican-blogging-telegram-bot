from packages.states.navigation.idlestate import IdleState
from packages.datamodel.poststate import PostState

__author__ = "aneanet"


class UpdateDraftState(IdleState):
    """
    Concrete state implementation.

    Lets the user select a draft for editing.
    """

    @property
    def welcome_message(self):
        return "Which <b>draft</b> do you want to <b>update</b>?"

    @property
    def callback_options(self):
        reply_options = []

        # for all user drafts show corresponding button
        user_drafts = self.context.get_user_posts(self.user_id, status=PostState.DRAFT)
        for post in user_drafts:
            reply_options.append({"text": post.title, "callback_data": "/updatedraft " + str(post.id)})

        # add button to return to main menu
        reply_options.append({"text": "<< main menu", "callback_data": "/mainmenu"})

        return reply_options

    def process_callback_query(self, user_id, chat_id, message_id, data):
        next_state = self
        command_array = data.split(" ")

        # only accept "/updatedraft <post_id>" callback queries
        if len(command_array) == 2 and command_array[0] == "/updatedraft":

            post_id = command_array[1]

            from packages.states.navigation.selectdraftupdatestate import SelectDraftUpdateState
            next_state = SelectDraftUpdateState(self.context, user_id, post_id, chat_id=chat_id, message_id=message_id)

        else:
            next_state = super().process_callback_query(user_id, chat_id, message_id, data)

        return next_state
