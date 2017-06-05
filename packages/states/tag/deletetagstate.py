from packages.bot.parsemode import ParseMode
from packages.states.navigation.selectdraftupdatestate import SelectDraftUpdateState
from packages.datamodel.poststate import PostState

__author__ = "aneanet"


class DeleteTagState(SelectDraftUpdateState):
    """
    Concrete state implementation.

    Lets the user select a tag for deletion.
    """

    @property
    def welcome_message(self):
        message = "It seems the draft you selected no longer exists..."

        post = self.context.get_post(self.post_id)
        if post is not None:
            message = "Which <b>tag</b> do you want to <b>delete</b> from draft <b>" + post.title + "</b>?"

        return message

    @property
    def callback_options(self):

        # add buttons to return to update option menu, draft list
        reply_options = [{"text": "<< update options", "callback_data": "/selectupdate"}
                        , {"text": "<< drafts", "callback_data": "/updatedraft"}]

        # show deletion button for every tag currently assigned to draft
        post_tags = self.context.get_post_tags(self.post_id)
        for tag in post_tags:
            reply_options.append({"text": tag.name, "callback_data": "/deleteposttag " + str(tag.id)})

        # add button to return to main menu, make sure it always covers entire width of table
        if len(reply_options) % 2 == 1:
            reply_options.append({})
        reply_options.append({"text": "<< main menu", "callback_data": "/mainmenu"})

        return reply_options

    def process_callback_query(self, user_id, chat_id, message_id, data):
        next_state = self
        command_array = data.split(" ")

        # only accept "/deleteposttag <tag_id>" callback queries
        if len(command_array) == 2 and command_array[0] == "/deleteposttag":

            tag_id = command_array[1]

            # check if previously selected post still exists
            post = self.context.get_post(self.post_id)
            if post is not None:

                deleted_tag = self.context.delete_post_tag(post.id, tag_id)

                # tag removal successful
                if deleted_tag is not None:
                    self.context.edit_message_text(chat_id, message_id
                                                    , "Tag <b>" + deleted_tag.name + "</b> has been <b>deleted</b> from draft <b>" + post.title + "</b>."
                                                    , parse_mode=ParseMode.HTML.value)
                # tag removal not successful
                else:
                    self.context.edit_message_text(chat_id, self.message_id
                                                   , "It seems the tag you selected no longer exists..."
                                                   , parse_mode=ParseMode.HTML.value)

                # show remaining tags for deletion
                if len(post.tags) - (1 if deleted_tag is not None else 0) > 0:
                    next_state = DeleteTagState(self.context, user_id, post.id, chat_id=chat_id)
                # no remaining tags -> automatically go back to update option menu
                else:
                    next_state = SelectDraftUpdateState(self.context, user_id, post.id, chat_id=chat_id)

            # previously selected post no longer exists
            else:
                self.context.send_message(chat_id
                                          , "It seems the draft you selected no longer exists..."
                                          , parse_mode=ParseMode.HTML.value)

                # show remaining drafts for updating
                user_drafts = self.context.get_user_posts(user_id=user_id, status=PostState.DRAFT)
                if len(user_drafts) > 0:
                    from packages.states.draft.updatedraftstate import DeleteDraftState
                    next_state = DeleteDraftState(self.context, user_id, chat_id=chat_id)
                # no remaining drafts -> automatically go back to main menu
                else:
                    from packages.states.navigation.idlestate import IdleState
                    next_state = IdleState(self.context, user_id, chat_id=chat_id)

        else:
            next_state = super().process_callback_query(user_id, chat_id, message_id, data)

        return next_state
