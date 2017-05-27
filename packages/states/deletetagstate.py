from packages.states.selectdraftupdatestate import SelectDraftUpdateState
from packages.bot.parsemode import ParseMode

__author__ = "aneanet"


class DeleteTagState(SelectDraftUpdateState):
    """
    Concrete state implementation.
    Lets the user select a tag for deletion.
    """

    @property
    def init_message(self):
        message = "It seems the draft you selected no longer exists..."

        user_drafts = self.context.get_posts(post_id=self.post_id)
        if len(user_drafts) > 0:
            post_title = user_drafts[0]["title"]
            message = "Which *tag* do you want to *delete* from draft *" + post_title + "*?"

        return message

    @property
    def initial_options(self):
        reply_options = [{"text": "<< update options", "callback_data": "/selectupdate"}
                        , {"text": "<< drafts", "callback_data": "/updatedraft"}]

        # show deletion button for every tag currently assigned to draft
        for post_tag in self.context.get_post_tag(post_id=self.post_id):
            tags = self.context.get_tag(tag_id=post_tag["tag_id"])
            for tag in tags:
                reply_options.append({"text": tag["name"], "callback_data": "/deleteposttag " + str(tag["tag_id"])})

        # make sure that "mainmenu" button always covers entire width of table
        if len(reply_options) % 2 == 1:
            reply_options.append({})
        reply_options.append({"text": "<< main menu", "callback_data": "/mainmenu"})

        return reply_options

    def process_callback_query(self, user_id, chat_id, message_id, data):
        command_array = data.split(" ")

        # only accept "/deleteposttag ..." callback queries, have super() handle everything else
        if len(command_array) > 1 and command_array[0] == "/deleteposttag":

            # tag selected for deletion - /deleteposttag <tag_id>
            if len(command_array) == 2:
                tag_id = command_array[1]

                user_drafts = self.context.get_posts(post_id=self.post_id)
                if len(user_drafts) > 0:
                    post_title = user_drafts[0]["title"]

                    tags = self.context.get_tag(tag_id=tag_id)
                    post_tags = self.context.get_post_tag(post_id=self.post_id, tag_id=tag_id)
                    if len(tags) > 0 and len(post_tags) > 0:
                        post_tag_id = post_tags[0]["post_tag_id"]
                        tag_name = tags[0]["name"]

                        self.context.delete_post_tag(post_tag_id)
                        self.context.edit_message_text(chat_id, message_id
                                                       ,
                                                       "Successfully deleted tag *" + tag_name + "* from draft *" + post_title + "*."
                                                       , parse_mode=ParseMode.MARKDOWN.value)

                    else:
                        self.context.edit_message_text(chat_id, self.message_id
                                                       , "It seems the tag you selected no longer exists..."
                                                       , parse_mode=ParseMode.MARKDOWN.value)

                    # show remaining tags for deletion
                    if len(self.context.get_post_tag(post_id=self.post_id)) > 0:
                        next_state = DeleteTagState(self.context, user_id, self.post_id, chat_id=chat_id)
                    # no remaining tags -> automatically go back to update option menu
                    else:
                        next_state = SelectDraftUpdateState(self.context, user_id, self.post_id, chat_id=chat_id)

                else:
                    self.context.edit_message_text(chat_id, self.message_id
                                                   , "It seems the draft you selected no longer exists..."
                                                   , parse_mode=ParseMode.MARKDOWN.value)

                    # show remaining drafts for deletion
                    if len(self.context.get_posts(user_id=user_id, status="draft")) > 0:
                        from packages.states.deletedraftstate import DeleteDraftState
                        next_state = DeleteDraftState(self.context, user_id, chat_id=chat_id)
                    # no remaining drafts -> automatically go back to main menu
                    else:
                        from packages.states.idlestate import IdleState
                        next_state = IdleState(self.context, user_id, chat_id=chat_id)

                self.context.set_user_state(user_id, next_state)

        else:
            super().process_callback_query(user_id, chat_id, message_id, data)
