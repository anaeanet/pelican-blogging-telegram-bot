from packages.states.abstractuserpoststate import AbstractUserPostState
from packages.states.idlestate import IdleState

__author__ = "aneanet"


class SelectUpdateState(AbstractUserPostState, IdleState):
    """
    Concrete state implementation.
    """

    @property
    def init_message(self):
        message = "It seems the draft you selected no longer exists..."
        user_drafts = self.context.get_posts(post_id=self.post_id, status="draft")
        if len(user_drafts) > 0:
            post_title = user_drafts[0]["title"]
            message = "What do you want to do with draft '*" + post_title + "*'?"
        return message

    @property
    def initial_options(self):
        reply_options = [{"text": "<< drafts", "callback_data": "/updatedraft"}]

        user_drafts = self.context.get_posts(post_id=self.post_id, user_id=self.user_id, status="draft")
        if len(user_drafts) > 0:
            reply_options.append({"text": "EDIT content", "callback_data": "/selectupdate /editcontent"})
            # TODO add more options here
        reply_options.append({"text": "<< main menu", "callback_data": "/mainmenu"})

        return reply_options

    def process_callback_query(self, user_id, chat_id, message_id, data):
        command_array = data.split(" ")

        # only accept "/selectupdate ..." callback queries, have super() handle everything else
        if len(command_array) > 1 and command_array[0] == "/selectupdate":

            # update-option was chosen for selected draft - /selectupdate <update-option>
            if len(command_array) == 2:

                if command_array[1] == "/editcontent":
                    # TODO
                    None

                # TODO add other update options

        else:
            super().process_callback_query(user_id, chat_id, message_id, data)
