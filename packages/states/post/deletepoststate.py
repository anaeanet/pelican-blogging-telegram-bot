from packages.states.navigation.idlestate import IdleState
from packages.datamodel.poststate import PostState

__author__ = "aneanet"


class DeletePostState(IdleState):
    """
    Concrete state implementation.

    Lets the user select a post for deletion.
    """

    @property
    def welcome_message(self):
        return "Which <b>post</b> do you want to <b>delete</b>?"

    @property
    def callback_options(self):
        reply_options = []

        # for all user posts show corresponding button
        user_posts = self.context.persistence.get_posts(user_id=self.user_id, status=PostState.PUBLISHED)
        for post in [p for p in user_posts if p.status == PostState.PUBLISHED]:

            # only allow deletion of published posts that do not already have a follow-up draft
            if post.id not in [draft.original_post for draft in user_posts if draft.status == PostState.DRAFT]:
                reply_options.append({"text": post.title, "callback_data": "/deletepost " + str(post.id)})

        # add button to return to main menu
        reply_options.append({"text": "<< main menu", "callback_data": "/mainmenu"})

        return reply_options

    def process_callback_query(self, user_id, chat_id, message_id, data):
        next_state = self
        command_array = data.split(" ")

        # only accept "/deletepost <post_id>" callback queries
        if len(command_array) == 2 and command_array[0] == "/deletepost":

            post_id = command_array[1]

            from packages.states.post.confirmpostdeletionstate import ConfirmPostDeletionState
            next_state = ConfirmPostDeletionState(self.context, user_id, post_id, chat_id=chat_id, message_id=message_id)

        else:
            next_state = super().process_callback_query(user_id, chat_id, message_id, data)

        return next_state
