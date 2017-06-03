from packages.states.navigation.idlestate import IdleState

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
        for post in self.context.get_posts(user_id=self.user_id, status="draft"):
            reply_options.append({"text": post["title"], "callback_data": "/deletedraft " + str(post["post_id"])})
        reply_options.append({"text": "<< main menu", "callback_data": "/mainmenu"})
        return reply_options

    def process_callback_query(self, user_id, chat_id, message_id, data):
        command_array = data.split(" ")

        # only accept "/deletedraft ..." callback queries, have super() handle everything else
        if len(command_array) > 1 and command_array[0] == "/deletedraft":

            # draft selected for deletion - /deletedraft <post_id>
            if len(command_array) == 2:
                post_id = command_array[1]

                from packages.states.draft.confirmdraftdeletionstate import ConfirmDraftDeletionState
                next_state = ConfirmDraftDeletionState(self.context, user_id, post_id, chat_id=chat_id, message_id=message_id)
                self.context.set_state(user_id, next_state)

        else:
            super().process_callback_query(user_id, chat_id, message_id, data)
