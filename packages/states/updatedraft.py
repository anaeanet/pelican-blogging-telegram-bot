from packages.states.idlestate import IdleState

__author__ = "aneanet"


class UpdateDraftState(IdleState):
    """
    Concrete state implementation.
    Let's the user select a draft for editing.
    """

    @property
    def init_message(self):
        return "Which draft do you want to *update*?"

    @property
    def initial_options(self):
        reply_options = []
        for post in self.context.get_posts(user_id=self.user_id, status="draft"):
            reply_options.append({"text": post["title"], "callback_data": "/updatedraft " + str(post["post_id"])})
        reply_options.append({"text": "<< main menu", "callback_data": "/mainmenu"})
        return reply_options

    def process_callback_query(self, user_id, chat_id, message_id, data):
        command_array = data.split(" ")

        # only accept "/updatedraft ..." callback queries, have super() handle everything else
        if len(command_array) > 1 and command_array[0] == "/updatedraft":

            # draft selected for deletion - /updatedraft <post_id>
            if len(command_array) == 2:
                post_id = command_array[1]

                from packages.states.selectupdatestate import SelectUpdateState
                next_state = SelectUpdateState(self.context, user_id, post_id, chat_id=chat_id, message_id=message_id)
                self.context.set_user_state(user_id, next_state)

        else:
            super().process_callback_query(user_id, chat_id, message_id, data)
