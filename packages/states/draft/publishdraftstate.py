from packages.bot.parsemode import ParseMode
from packages.states.navigation.selectdraftupdatestate import SelectDraftUpdateState
from packages.datamodel.poststate import PostState

__author__ = "aneanet"


class PublishDraftState(SelectDraftUpdateState):
    """
    Concrete state implementation.

    Accepts user choice to publish a current draft either as draft or final post.
    """

    @property
    def welcome_message(self):
        message = "It seems the draft you selected no longer exists..."

        post = self.bot.persistence.get_post(self.post_id)
        if post is not None:
            message = "<b>Publish " + post.title + " as draft</b> to (p)review it on the blog. " \
                      + "Once you are happy with it, come back here to <b>publish as post</b>."

        return message

    @property
    def callback_options(self):

        # add buttons to return to update option menu, draft list
        reply_options = [{"text": "<< update options", "callback_data": "/selectupdate"}
                        , {"text": "<< drafts", "callback_data": "/updatedraft"}]

        # show button for each publish option
        post = self.bot.persistence.get_post(self.post_id)
        if post is not None:
            reply_options.append({"text": "PUBLISH as draft", "callback_data": "/publish " + PostState.DRAFT.value})

            # only show "publish as post" if draft has already been published as draft to (p)review
            if post.tmsp_publish is not None:
                reply_options.append({"text": "PUBLISH as post", "callback_data": "/publish " + PostState.PUBLISHED.value})

        # add button to return to main menu, make sure it always covers entire width of table
        if len(reply_options) % 2 == 1:
            reply_options.append({})
        reply_options.append({"text": "<< main menu", "callback_data": "/mainmenu"})

        return reply_options

    def process_callback_query(self, user_id, chat_id, message_id, data):
        next_state = self
        command_array = data.split(" ")

        # only accept "/publish <draft/published>" callback queries
        if len(command_array) == 2 and command_array[0] == "/publish" and command_array[1] in [state.value for state in PostState]:

            publish_type = command_array[1]

            # check if previously selected post still exists
            post = self.bot.persistence.get_post(self.post_id)
            if post is not None:

                is_published = self.bot.publish(post.id, PostState(publish_type))

                # publishing successful
                if is_published:
                    self.bot.edit_message_text(chat_id, message_id
                                               , "<b>" + post.title + "</b> has been <b>published</b> as <b>"
                                               + ("draft" if publish_type == PostState.DRAFT.value else "final post") + "</b>."
                                               , parse_mode=ParseMode.HTML.value)

                    # if published as post -> go back to main menu
                    if publish_type == PostState.PUBLISHED.value:
                        from packages.states.navigation.idlestate import IdleState
                        next_state = IdleState(self.bot, user_id, chat_id=chat_id)
                    else:
                        next_state = SelectDraftUpdateState(self.bot, user_id, post.id, chat_id=chat_id)

                # publishing not successful
                else:
                    self.bot.edit_message_text(chat_id, self.message_id
                                               , "It seems publishing is not possible..."
                                               , parse_mode=ParseMode.HTML.value)
                    next_state = PublishDraftState(self.bot, user_id, post.id, chat_id=chat_id)

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

        else:
            next_state = super().process_callback_query(user_id, chat_id, message_id, data)

        return next_state
