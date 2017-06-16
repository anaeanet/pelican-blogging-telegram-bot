from packages.states.navigation.idlestate import IdleState
from packages.datamodel.poststate import PostState

__author__ = "aneanet"


class UpdatePostState(IdleState):
    """
    Concrete state implementation.

    Lets the user select a post for editing.
    """

    @property
    def welcome_message(self):
        return "Which <b>post</b> do you want to <b>update</b>?"

    @property
    def callback_options(self):
        reply_options = []

        user_posts = self.context.persistence.get_posts(user_id=self.user_id)

        # show button for every published post that does not have a follow-up draft/post
        published_posts = [post for post in user_posts if post.status == PostState.PUBLISHED]
        base_post_ids = [post.original_post.id for post in user_posts if post.original_post is not None]
        for post in [p for p in published_posts if p.id not in base_post_ids]:
            reply_options.append({"text": post.title, "callback_data": "/updatepost " + str(post.id)})

        # add button to return to main menu
        reply_options.append({"text": "<< main menu", "callback_data": "/mainmenu"})

        return reply_options

    def process_callback_query(self, user_id, chat_id, message_id, data):
        next_state = self
        command_array = data.split(" ")

        # only accept "/updatepost <post_id>" callback queries
        if len(command_array) == 2 and command_array[0] == "/updatepost":

            post_id = command_array[1]

            from packages.states.post.confirmpostupdatestate import ConfirmPostUpdateState
            next_state = ConfirmPostUpdateState(self.context, user_id, post_id, chat_id=chat_id, message_id=message_id)

        else:
            next_state = super().process_callback_query(user_id, chat_id, message_id, data)

        return next_state
