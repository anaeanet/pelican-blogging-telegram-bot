from packages.bot.parsemode import ParseMode
from packages.states.abstract.abstractuserpoststate import AbstractUserPostState
from packages.states.navigation.idlestate import IdleState

__author__ = "aneanet"


class ConfirmDraftDeletionState(AbstractUserPostState, IdleState):
    """
    Concrete state implementation.
    Lets the user confirm or abort deletion of a previously chosen draft.
    """

    @property
    def welcome_message(self):
        message = "It seems the draft you selected no longer exists..."
        user_drafts = self.context.get_posts(post_id=self.post_id)
        if len(user_drafts) > 0:
            post_title = user_drafts[0]["title"]
            message = "Do you <b>really</b> want to <b>delete</b> draft <b>" + post_title + "</b>?"
        return message

    @property
    def callback_options(self):
        reply_options = [{"text": "<< drafts", "callback_data": "/deletedraft"}]

        user_drafts = self.context.get_posts(post_id=self.post_id)
        if len(user_drafts) > 0:
            reply_options.append({"text": "Yes, delete", "callback_data": "/confirmdraftdeletion /confirm"})
        reply_options.append({"text": "<< main menu", "callback_data": "/mainmenu"})

        return reply_options

    def process_callback_query(self, user_id, chat_id, message_id, data):
        command_array = data.split(" ")

        # only accept "/confirmdraftdeletion ..." callback queries, have super() handle everything else
        if len(command_array) > 1 and command_array[0] == "/confirmdraftdeletion":

            # deletion of draft confirmed or aborted - /confirmdraftdeletion <confirm/back>
            if len(command_array) == 2:

                # confirmed draft deletion
                if command_array[1] == "/confirm":

                    user_drafts = self.context.get_posts(post_id=self.post_id)
                    if len(user_drafts) > 0:
                        post_title = user_drafts[0]["title"]
                        self.context.delete_post(self.post_id)
                        self.context.edit_message_text(chat_id, message_id
                                                             , "Draft <b>" + post_title + "</b> has been <b>deleted</b>."
                                                             , parse_mode=ParseMode.HTML.value)

                    else:
                        self.context.edit_message_text(chat_id, self.message_id
                                                  , "It seems the draft you selected no longer exists..."
                                                  , parse_mode=ParseMode.HTML.value)

                    # show remaining drafts for deletion
                    if len(self.context.get_posts(user_id=user_id, status="draft")) > 0:
                        from packages.states.draft.deletedraftstate import DeleteDraftState
                        next_state = DeleteDraftState(self.context, user_id, chat_id=chat_id)
                    # no remaining drafts -> automatically go back to main menu
                    else:
                        next_state = IdleState(self.context, user_id, chat_id=chat_id)

                    self.context.set_state(user_id, next_state)

        else:
            super().process_callback_query(user_id, chat_id, message_id, data)
