from packages.states.abstractuserpoststate import AbstractUserPostState
from packages.states.idlestate import IdleState

__author__ = "aneanet"


class SelectDraftUpdateState(AbstractUserPostState, IdleState):
    """
    Concrete state implementation.
    Lets the user select what to change on a previously chosen draft.
    """

    @property
    def init_message(self):
        message = "It seems the draft you selected no longer exists..."
        user_drafts = self.context.get_posts(post_id=self.post_id, user_id=self.user_id, status="draft")
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
            reply_options.append({"text": "ADD tag(s)", "callback_data": "/selectupdate /addtag"})
            # TODO only show this button if post already has tags, otheriwse add empty option
            reply_options.append({"text": "DELETE tag(s)", "callback_data": "/selectupdate /deletetag"})
            reply_options.append({"text": "ADD image(s)", "callback_data": "/selectupdate /addimage"})
            # TODO only show this button if post already has images, otheriwse add empty option
            reply_options.append({"text": "DELETE image(s)", "callback_data": "/selectupdate /deleteimage"})
            reply_options.append({"text": "SET title pic", "callback_data": "/selectupdate /settitlepic"})
            # TODO only show this button if post already has title picture, otheriwse add empty option
            reply_options.append({"text": "DELETE title pic", "callback_data": "/selectupdate /deletetitlepic"})
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
                elif command_array[1] == "/addtag":
                    # TODO
                    None
                elif command_array[1] == "/deletetag":
                    # TODO
                    None
                elif command_array[1] == "/addimage":
                    # TODO
                    None
                elif command_array[1] == "/deleteimage":
                    # TODO
                    None
                elif command_array[1] == "/settitlepic":
                    # TODO
                    None
                elif command_array[1] == "/deletetitlepic":
                    # TODO
                    None

        else:
            super().process_callback_query(user_id, chat_id, message_id, data)
