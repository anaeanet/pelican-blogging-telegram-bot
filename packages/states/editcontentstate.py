from packages.states.selectdraftupdatestate import SelectDraftUpdateState
from packages.bot.parsemode import ParseMode

__author__ = "aneanet"


class EditContentState(SelectDraftUpdateState):
    """
    Concrete state implementation.
    Accepts plain text message as new content of draft/post.
    """

    @property
    def init_message(self):
        message = "It seems the draft you selected no longer exists..."

        user_drafts = self.context.get_posts(post_id=self.post_id, user_id=self.user_id)
        if len(user_drafts) > 0:
            post_title = user_drafts[0]["title"]
            post_content = user_drafts[0]["content"]

            if post_content is not None and len(post_content) > 0:
                message = "Just type away to replace the current content of draft '*" + post_title + "*' or copy from above and edit."
                message = "You have the following options to modify the content of draft '*" + post_title + "*':" \
                            + "\r\n" + "*replace* content - just type away" \
                            + "\r\n" + "*update* content - copy and edit" \
                            + "\r\n" + "*append* content - type /append <text>"
            else:
                message = "Draft '*" + post_title + "*' does not have any content yet. Just type away to add new content."

        return message

    @property
    def initial_options(self):
        reply_options = [{"text": "<< update options", "callback_data": "/selectupdate"}
                        , {"text": "<< drafts", "callback_data": "/updatedraft"}
                        , {"text": "<< main menu", "callback_data": "/mainmenu"}]
        return reply_options

    def process_message(self, user_id, chat_id, text):
        if text.startswith("/") and not text.startswith("/append"):
            super().process_message(user_id, chat_id, text)
        else:
            # remove inline keyboard from latest bot message (by leaving out reply_options parameter)
            self.build_state_message(chat_id, self.init_message, message_id=self.message_id)

            user_drafts = self.context.get_posts(post_id=self.post_id, user_id=self.user_id)
            if len(user_drafts) > 0:
                post_title = user_drafts[0]["title"]
                post_content = user_drafts[0]["content"]

                if text.startswith("/append"):
                    new_content = post_content + " " + text.split("/append")[1].strip(' ')
                else:
                    new_content = text

                self.context.update_post(self.post_id, content=new_content)
                self.context.send_message(chat_id, "Content of draft '*" + post_title + "*' updated successfully."
                                          , parse_mode=ParseMode.MARKDOWN.value)
                next_state = SelectDraftUpdateState(self.context, user_id, self.post_id, chat_id=chat_id)

            else:
                self.context.send_message(chat_id
                                          , "It seems the draft you selected no longer exists..."
                                          , parse_mode=ParseMode.MARKDOWN.value)

                # show remaining drafts for updating
                if len(self.context.get_posts(user_id=user_id, status="draft")) > 0:
                    from packages.states.updatedraftstate import UpdateDraftState
                    next_state = UpdateDraftState(self.context, user_id, chat_id=chat_id)
                # no remaining drafts -> automatically go back to main menu
                else:
                    from packages.states.idlestate import IdleState
                    next_state = IdleState(self.context, user_id, chat_id=chat_id)

            self.context.set_user_state(user_id, next_state)
