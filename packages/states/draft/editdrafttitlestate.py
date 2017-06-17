from packages.bot.parsemode import ParseMode
from packages.states.navigation.selectdraftupdatestate import SelectDraftUpdateState
from packages.datamodel.poststate import PostState

__author__ = "aneanet"


class EditDraftTitleState(SelectDraftUpdateState):
    """
    Concrete state implementation.

    Accepts plain text message as new title of draft/post.
    """

    @property
    def welcome_message(self):
        message = "It seems the draft you selected no longer exists..."

        post = self.bot.persistence.get_post(self.post_id)
        if post is not None:
            message = "Enter the <b>new title</b> of draft <b>" + post.title + "</b>:"

        return message

    @property
    def callback_options(self):
        # add buttons to return to update option menu, draft list, or main menu
        return [{"text": "<< update options", "callback_data": "/selectupdate"}
            , {"text": "<< drafts", "callback_data": "/updatedraft"}
            , {"text": "<< main menu", "callback_data": "/mainmenu"}]

    def process_message(self, user_id, chat_id, text, entities):
        next_state = self
        text = text.strip(' \t\n\r')

        # let super() handle any bot commands
        if text.startswith("/") or "bot_command" in [entity["type"] for entity in entities]:
            next_state = super().process_message(user_id, chat_id, text, entities)

        # accept simple text as new post title
        else:
            # remove inline keyboard from latest bot message (by leaving out reply_options parameter)
            self.build_state_message(chat_id, self.welcome_message, message_id=self.message_id)

            # check if previously selected post still exists
            post = self.bot.persistence.get_post(self.post_id)
            if post is not None:
                new_title = text

                updated_post = self.bot.persistence.update_post(post.id, post.user.id, new_title, post.status
                                                                , post.gallery.title
                                                                , post.content
                                                                , None if post.title_image is None else post.title_image.id
                                                                , post.tmsp_publish
                                                                , None if post.original_post is None else post.original_post.id)

                # post update successful
                if updated_post is not None:
                    self.bot.send_message(chat_id
                                          , "Draft title has been updated to <b>" + updated_post.title + "</b>."
                                          , parse_mode=ParseMode.HTML.value)
                # post update not successful
                else:
                    self.bot.send_message(chat_id
                                          , "Draft title could not be updated."
                                          , parse_mode=ParseMode.HTML.value)

                next_state = SelectDraftUpdateState(self.bot, user_id, self.post_id, chat_id=chat_id)

            # previously selected post no longer exists
            else:
                self.bot.send_message(chat_id
                                      , "It seems the draft you selected no longer exists..."
                                      , parse_mode=ParseMode.HTML.value)

                # show remaining drafts for updating
                user_drafts = self.bot.persistence.get_posts(user_id=user_id, status=PostState.DRAFT)
                if len(user_drafts) > 0:
                    from packages.states.draft.updatedraftstate import UpdateDraftState
                    next_state = UpdateDraftState(self.bot, user_id, chat_id=chat_id)
                # no remaining drafts -> automatically go back to main menu
                else:
                    from packages.states.navigation.idlestate import IdleState
                    next_state = IdleState(self.bot, user_id, chat_id=chat_id)

        return next_state
