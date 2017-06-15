from packages.bot.parsemode import ParseMode
from packages.states.navigation.selectdraftupdatestate import SelectDraftUpdateState
from packages.datamodel.poststate import PostState

__author__ = "aneanet"


class ConfirmDraftDeletionState(SelectDraftUpdateState):
    """
    Concrete state implementation.

    Lets the user confirm or abort deletion of a previously chosen draft.
    """

    @property
    def welcome_message(self):
        message = "It seems the draft you selected no longer exists..."

        post = self.context.persistence.get_post(self.post_id)
        if post is not None:
            message = "Do you <b>really</b> want to <b>delete</b> draft <b>" + post.title + "</b>?"

        return message

    @property
    def callback_options(self):

        # add button to return to draft list
        reply_options = [{"text": "<< drafts", "callback_data": "/deletedraft"}, []]

        # if post still exists, show button to confirm final deletion
        post = self.context.persistence.get_post(self.post_id)
        if post is not None:
            reply_options.append({"text": "YES, delete", "callback_data": "/confirmdraftdeletion /confirm"})
            reply_options.append([])

        # add button to return to main menu
        reply_options.append({"text": "<< main menu", "callback_data": "/mainmenu"})

        return reply_options

    def process_callback_query(self, user_id, chat_id, message_id, data):
        next_state = self
        command_array = data.split(" ")

        # only accept "/confirmdraftdeletion <confirm/back>" callback queries
        if len(command_array) == 2 and command_array[0] == "/confirmdraftdeletion":

            # confirmed draft deletion
            if command_array[1] == "/confirm":


                deleted_post = self.context.persistence.delete_post(self.post_id) if self.context.unpublish(self.post_id) else None

                # post removal successful
                if deleted_post is not None:
                    self.context.edit_message_text(chat_id, message_id
                                                   , "Draft <b>" + deleted_post.title + "</b> has been <b>deleted</b>."
                                                   , parse_mode=ParseMode.HTML.value)
                # post removal not successful
                else:
                    self.context.edit_message_text(chat_id, self.message_id
                                              , "It seems the draft you selected no longer exists..."
                                              , parse_mode=ParseMode.HTML.value)

                # show remaining drafts for deletion
                user_drafts = self.context.persistence.get_posts(user_id=user_id, status=PostState.DRAFT)
                if len(user_drafts) > 0:
                    from packages.states.draft.deletedraftstate import DeleteDraftState
                    next_state = DeleteDraftState(self.context, user_id, chat_id=chat_id)
                # no remaining drafts -> automatically go back to main menu
                else:
                    from packages.states.navigation.idlestate import IdleState
                    next_state = IdleState(self.context, user_id, chat_id=chat_id)

        else:
            next_state = super().process_callback_query(user_id, chat_id, message_id, data)

        return next_state
