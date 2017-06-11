from packages.bot.parsemode import ParseMode
from packages.states.navigation.selectdraftupdatestate import SelectDraftUpdateState
from packages.datamodel.poststate import PostState

__author__ = "aneanet"


class ConfirmPostUpdateState(SelectDraftUpdateState):
    """
    Concrete state implementation.

    Lets the user confirm update of previously published post, i.e. creation of new draft.
    """

    @property
    def welcome_message(self):
        message = "It seems the post you selected no longer exists..."

        post = self.context.get_post(self.post_id)
        if post is not None:
            message = "Do you <b>really</b> want to <b>update</b> post <b>" + post.title + "</b>?"

        return message

    @property
    def callback_options(self):

        # add button to return to post list
        reply_options = [{"text": "<< drafts", "callback_data": "/deletepost"}, []]

        # if post still exists, show button to confirm final deletion
        post = self.context.get_post(self.post_id)
        if post is not None:
            reply_options.append({"text": "YES, update", "callback_data": "/confirmpostupdate /confirm"})
            reply_options.append([])

        # add button to return to main menu
        reply_options.append({"text": "<< main menu", "callback_data": "/mainmenu"})

        return reply_options

    def process_callback_query(self, user_id, chat_id, message_id, data):
        next_state = self
        command_array = data.split(" ")

        # only accept "/confirmpostupdate <confirm/back>" callback queries
        if len(command_array) == 2 and command_array[0] == "/confirmpostupdate":

            # confirmed post update
            if command_array[1] == "/confirm":

                new_draft = self.context.copy_post(self.post_id)

                # draft creation successful
                if new_draft is not None:
                    self.context.edit_message_text(chat_id, message_id
                                                   , "New draft for modification of post <b>" + new_draft.title + "</b> has been <b>created</b>."
                                                   , parse_mode=ParseMode.HTML.value)

                    # show update options for newly created draft
                    from packages.states.navigation.selectdraftupdatestate import SelectDraftUpdateState
                    next_state = SelectDraftUpdateState(self.context, user_id, new_draft.id, chat_id=chat_id)

                # draft creation not successful
                else:
                    self.context.edit_message_text(chat_id, self.message_id
                                              , "It seems the post you selected cannot be updated..."
                                              , parse_mode=ParseMode.HTML.value)

                    # go back to menu showing existing published posts
                    from packages.states.post.updatepoststate import UpdatePostState
                    next_state = UpdatePostState(self.context, user_id, chat_id=chat_id)

        else:
            next_state = super().process_callback_query(user_id, chat_id, message_id, data)

        return next_state
