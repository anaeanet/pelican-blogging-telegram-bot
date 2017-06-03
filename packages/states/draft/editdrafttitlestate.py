from packages.bot.parsemode import ParseMode
from packages.states.navigation.selectdraftupdatestate import SelectDraftUpdateState

__author__ = "aneanet"


class EditDraftTitleState(SelectDraftUpdateState):
    """
    Concrete state implementation.
    Accepts plain text message as new content of draft/post.
    """

    @property
    def welcome_message(self):
        message = "It seems the draft you selected no longer exists..."

        user_drafts = self.context.get_posts(post_id=self.post_id)
        if len(user_drafts) > 0:
            post_title = user_drafts[0]["title"]
            post_content = user_drafts[0]["content"]

            if post_content is not None and len(post_content) > 0:
                message = "Enter the <b>new title</b> of draft <b>" + post_title + "</b>:"

        return message

    @property
    def callback_options(self):
        reply_options = [{"text": "<< update options", "callback_data": "/selectupdate"}
                        , {"text": "<< drafts", "callback_data": "/updatedraft"}
                        , {"text": "<< main menu", "callback_data": "/mainmenu"}]

        return reply_options

    def process_message(self, user_id, chat_id, text, entities):
        if text.startswith("/"):
            super().process_message(user_id, chat_id, text, entities)
        else:
            # remove inline keyboard from latest bot message (by leaving out reply_options parameter)
            self.build_state_message(chat_id, self.welcome_message, message_id=self.message_id)

            user_drafts = self.context.get_posts(post_id=self.post_id)
            if len(user_drafts) > 0:
                post_title = text.strip(' \t\n\r')

                # update post title
                self.context.update_post(self.post_id, title=post_title)
                self.context.send_message(chat_id
                                          , "Draft title has been updated to <b>" + post_title + "</b>."
                                          , parse_mode=ParseMode.HTML.value)
                next_state = SelectDraftUpdateState(self.context, user_id, self.post_id, chat_id=chat_id)

            else:
                self.context.send_message(chat_id
                                          , "It seems the draft you selected no longer exists..."
                                          , parse_mode=ParseMode.HTML.value)

                # show remaining drafts for updating
                if len(self.context.get_posts(user_id=user_id, status="draft")) > 0:
                    from packages.states.draft.updatedraftstate import UpdateDraftState
                    next_state = UpdateDraftState(self.context, user_id, chat_id=chat_id)
                # no remaining drafts -> automatically go back to main menu
                else:
                    from packages.states.navigation.idlestate import IdleState
                    next_state = IdleState(self.context, user_id, chat_id=chat_id)

            self.context.set_state(user_id, next_state)
