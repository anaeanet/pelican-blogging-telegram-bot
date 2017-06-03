from packages.bot.parsemode import ParseMode
from packages.states.navigation.selectdraftupdatestate import SelectDraftUpdateState

__author__ = "aneanet"


class DeleteTagState(SelectDraftUpdateState):
    """
    Concrete state implementation.
    Lets the user select a tag for deletion.
    """

    @property
    def welcome_message(self):
        message = "It seems the draft you selected no longer exists..."

        user_drafts = self.context.get_posts(post_id=self.post_id)
        if len(user_drafts) > 0:
            post_title = user_drafts[0]["title"]
            message = "Which <b>tag</b> do you want to <b>delete</b> from draft <b>" + post_title + "</b>?"

        return message

    @property
    def callback_options(self):
        reply_options = [{"text": "<< update options", "callback_data": "/selectupdate"}
                        , {"text": "<< drafts", "callback_data": "/updatedraft"}]

        # show deletion button for every tag currently assigned to draft
        for post_tag in self.context.get_post_tags(post_id=self.post_id):
            tags = self.context.get_tags(tag_id=post_tag["tag_id"])
            for tag in tags:
                reply_options.append({"text": tag["name"], "callback_data": "/deleteposttag " + str(tag["tag_id"])})

        # make sure that "mainmenu" button always covers entire width of table
        if len(reply_options) % 2 == 1:
            reply_options.append({})
        reply_options.append({"text": "<< main menu", "callback_data": "/mainmenu"})

        return reply_options

    def process_callback_query(self, user_id, chat_id, message_id, data):
        next_state = self
        command_array = data.split(" ")

        # only accept "/deleteposttag ..." callback queries, have super() handle everything else
        if len(command_array) > 1 and command_array[0] == "/deleteposttag":

            # tag selected for deletion - /deleteposttag <tag_id>
            if len(command_array) == 2:
                tag_id = command_array[1]

                user_drafts = self.context.get_posts(post_id=self.post_id)
                if len(user_drafts) > 0:
                    post_title = user_drafts[0]["title"]

                    tags = self.context.get_tags(tag_id=tag_id)
                    post_tags = self.context.get_post_tags(post_id=self.post_id, tag_id=tag_id)
                    if len(tags) > 0 and len(post_tags) > 0:
                        post_tag_id = post_tags[0]["post_tag_id"]
                        tag_name = tags[0]["name"]

                        self.context.delete_post_tag(post_tag_id)
                        self.context.edit_message_text(chat_id, message_id
                                                       ,
                                                       "Tag <b>" + tag_name + "</b> has been <b>deleted</b> from draft <b>" + post_title + "</b>."
                                                       , parse_mode=ParseMode.HTML.value)

                    else:
                        self.context.edit_message_text(chat_id, self.message_id
                                                       , "It seems the tag you selected no longer exists..."
                                                       , parse_mode=ParseMode.HTML.value)

                    # show remaining tags for deletion
                    if len(self.context.get_post_tags(post_id=self.post_id)) > 0:
                        next_state = DeleteTagState(self.context, user_id, self.post_id, chat_id=chat_id)
                    # no remaining tags -> automatically go back to update option menu
                    else:
                        next_state = SelectDraftUpdateState(self.context, user_id, self.post_id, chat_id=chat_id)

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
                        from packages.states.navigation.idlestate import IdleState
                        next_state = IdleState(self.context, user_id, chat_id=chat_id)

        else:
            next_state = super().process_callback_query(user_id, chat_id, message_id, data)

        return next_state
