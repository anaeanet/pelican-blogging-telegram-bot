from packages.bot.parsemode import ParseMode
from packages.states.navigation.selectdraftupdatestate import SelectDraftUpdateState

__author__ = "aneanet"


class EditContentState(SelectDraftUpdateState):
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
                message = "To <b>modify the content</b> of draft <b>" + post_title + "</b> use one of the following three options:" \
                            + "\r\n\r\n" \
                            + "<b>replace</b> content - just type away\r\n" \
                            + "<b>update</b> content - preview, copy & paste, edit\r\n" \
                            + "<b>append</b> content - type /append &lt;text&gt;"
            else:
                message = "Draft <b>" + post_title + "</b> does not have any content yet." \
                            + "\r\n\r\n" \
                            + "Just type away to <b>add new content</b>."

        return message

    @property
    def callback_options(self):
        reply_options = [{"text": "<< update options", "callback_data": "/selectupdate"}
                        , {"text": "<< drafts", "callback_data": "/updatedraft"}
                        , {"text": "INFO markdown", "callback_data": "/formatting"}, []]

        # if there already is some content, show "preview" button
        user_drafts = self.context.get_posts(post_id=self.post_id)
        if len(user_drafts) > 0 and user_drafts[0]["content"]:
            reply_options.append({"text": "PREVIEW content", "callback_data": "/previewcontent"})
            reply_options.append([])

        reply_options.append({"text": "<< main menu", "callback_data": "/mainmenu"})

        return reply_options

    def process_callback_query(self, user_id, chat_id, message_id, data):
        command_array = data.split(" ")

        # only accept "/previewcontent" callback queries, have super() handle everything else
        if len(command_array) == 1 and command_array[0] == "/previewcontent":

            user_drafts = self.context.get_posts(post_id=self.post_id)
            if len(user_drafts) > 0:
                post_content = user_drafts[0]["content"]

                # replace edit instructions with current draft content
                self.context.edit_message_text(chat_id, self.message_id
                                               , post_content)
                next_state = EditContentState(self.context, user_id, self.post_id, chat_id=chat_id)

            else:
                self.context.edit_message_text(chat_id, self.message_id
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

        # only accept "/formatting" callback queries, have super() handle everything else
        if len(command_array) == 1 and command_array[0] == "/formatting":

            user_drafts = self.context.get_posts(post_id=self.post_id)
            if len(user_drafts) > 0:
                message = "Following <b>Markdown</b> options are supported:\r\n\r\n" \
                    + "Headline: #..# text\r\n" \
                    + "Bold text: <b>**text**</b>\r\n" \
                    + "Italic text: <i>*text*</i>\r\n" \
                    + "Web link: [text](http://www.example.com/)\r\n" \
                    + "Inline code: <code>`some code`</code>\r\n" \
                    + "Pre-formatted code block <pre>```some code```</pre>"

                # replace edit instructions with Markdown formatting options
                self.context.edit_message_text(chat_id, self.message_id, message, parse_mode=ParseMode.HTML.value)
                next_state = EditContentState(self.context, user_id, self.post_id, chat_id=chat_id)

            else:
                self.context.edit_message_text(chat_id, self.message_id
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

        else:
            super().process_callback_query(user_id, chat_id, message_id, data)

    def process_message(self, user_id, chat_id, text, entities):
        if text.startswith("/") and not text.startswith("/append"):
            super().process_message(user_id, chat_id, text, entities)
        else:
            # remove inline keyboard from latest bot message (by leaving out reply_options parameter)
            self.build_state_message(chat_id, self.welcome_message, message_id=self.message_id)

            user_drafts = self.context.get_posts(post_id=self.post_id)
            if len(user_drafts) > 0:
                post_title = user_drafts[0]["title"]
                post_content = user_drafts[0]["content"]

                if text.startswith("/append"):
                    additional_text = text.split("/append")[1].strip(' ')
                    new_content = post_content + " " + additional_text
                else:
                    new_content = text

                self.context.update_post(self.post_id, content=new_content)
                self.context.send_message(chat_id, "Draft <b>" + post_title + "</b> has been updated with <b>new content</b>."
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
