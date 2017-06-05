from packages.bot.parsemode import ParseMode
from packages.states.navigation.selectdraftupdatestate import SelectDraftUpdateState
from packages.datamodel.poststate import PostState

__author__ = "aneanet"


class EditContentState(SelectDraftUpdateState):
    """
    Concrete state implementation.

    Accepts plain text message as new content of draft/post.
    """

    @property
    def welcome_message(self):
        message = "It seems the draft you selected no longer exists..."

        post = self.context.get_post(self.post_id)
        if post is not None:

            # content is not empty
            if len(post.content) > 0:
                message = "To <b>modify the content</b> of draft <b>" + post.title + "</b> use one of the following three options:" \
                            + "\r\n\r\n" \
                            + "<b>replace</b> content - just type away\r\n" \
                            + "<b>update</b> content - preview, copy & paste, edit\r\n" \
                            + "<b>append</b> content - type /append &lt;text&gt;"
            # content empty
            else:
                message = "Draft <b>" + post.title + "</b> does not have any content yet." \
                            + "\r\n\r\n" \
                            + "Just type away to <b>add new content</b>."

        return message

    @property
    def callback_options(self):
        # add buttons to return to update option menu, draft list, or show info about markdown syntax
        reply_options = [{"text": "<< update options", "callback_data": "/selectupdate"}
                        , {"text": "<< drafts", "callback_data": "/updatedraft"}
                        , {"text": "INFO markdown", "callback_data": "/formatting"}, []]

        # if content is not empty, show "preview" button
        post = self.context.get_post(self.post_id)
        if post is not None and len(post.content) > 0:
            reply_options.append({"text": "PREVIEW content", "callback_data": "/previewcontent"})
            reply_options.append([])

        # add buttons to return to main menu
        reply_options.append({"text": "<< main menu", "callback_data": "/mainmenu"})

        return reply_options

    def process_callback_query(self, user_id, chat_id, message_id, data):
        next_state = self
        command_array = data.split(" ")

        # only accept "/previewcontent" callback queries
        if len(command_array) == 1 and command_array[0] == "/previewcontent":

            # check if previously selected post still exists
            post = self.context.get_post(self.post_id)
            if post is not None:

                # replace edit instructions with current draft content
                self.context.edit_message_text(chat_id, self.message_id, post.content)

                next_state = EditContentState(self.context, user_id, post.id, chat_id=chat_id)

            # previously selected post no longer exists
            else:
                self.context.send_message(chat_id
                                          , "It seems the draft you selected no longer exists..."
                                          , parse_mode=ParseMode.HTML.value)

                # show remaining drafts for updating
                user_drafts = self.context.get_user_posts(user_id=user_id, status=PostState.DRAFT)
                if len(user_drafts) > 0:
                    from packages.states.draft.updatedraftstate import UpdateDraftState
                    next_state = UpdateDraftState(self.context, user_id, chat_id=chat_id)
                # no remaining drafts -> automatically go back to main menu
                else:
                    from packages.states.navigation.idlestate import IdleState
                    next_state = IdleState(self.context, user_id, chat_id=chat_id)

        # only accept "/formatting" callback queries
        elif len(command_array) == 1 and command_array[0] == "/formatting":

            # check if previously selected post still exists
            post = self.context.get_post(self.post_id)
            if post is not None:

                message = "Following <b>Markdown</b> options are supported:\r\n\r\n" \
                    + "Heading 1-6: #..# text\r\n" \
                    + "Bold text: <b>**text**</b>\r\n" \
                    + "Italic text: <i>*text*</i>\r\n" \
                    + "Web link: [text](http://www.example.com/)\r\n" \
                    + "Inline code: <code>`some code`</code>\r\n" \
                    + "Pre-formatted code block <pre>```some code```</pre>"

                # replace edit instructions with Markdown formatting options
                self.context.edit_message_text(chat_id, self.message_id, message, parse_mode=ParseMode.HTML.value)

                next_state = EditContentState(self.context, user_id, post.id, chat_id=chat_id)

            # previously selected post no longer exists
            else:
                self.context.send_message(chat_id
                                          , "It seems the draft you selected no longer exists..."
                                          , parse_mode=ParseMode.HTML.value)

                # show remaining drafts for updating
                user_drafts = self.context.get_user_posts(user_id=user_id, status=PostState.DRAFT)
                if len(user_drafts) > 0:
                    from packages.states.draft.updatedraftstate import UpdateDraftState
                    next_state = UpdateDraftState(self.context, user_id, chat_id=chat_id)
                # no remaining drafts -> automatically go back to main menu
                else:
                    from packages.states.navigation.idlestate import IdleState
                    next_state = IdleState(self.context, user_id, chat_id=chat_id)

        else:
            next_state = super().process_callback_query(user_id, chat_id, message_id, data)

        return next_state

    def process_message(self, user_id, chat_id, text, entities):
        next_state = self
        text = text.strip(' \t\n\r')

        # let super() handle any bot commands
        if (text.startswith("/") or "bot_command" in [entity["type"] for entity in entities]) and not text.startswith("/append"):
            next_state = super().process_message(user_id, chat_id, text, entities)

        # accept simple text as new post title
        else:
            # remove inline keyboard from latest bot message (by leaving out reply_options parameter)
            self.build_state_message(chat_id, self.welcome_message, message_id=self.message_id)

            # check if previously selected post still exists
            post = self.context.get_post(self.post_id)
            if post is not None:

                if text.startswith("/append"):
                    text_parts = text.split("/append")
                    if len(text_parts) == 2:
                        additional_content = text_parts[1].strip(' ')
                        new_content = post.content + " " + additional_content
                    else:
                        new_content = post.content
                else:
                    new_content = text

                updated_post = self.context.update_post(post.id, content=new_content)

                # post update successful
                if updated_post is not None:
                    self.context.send_message(chat_id
                                              , "Draft <b>" + post.title + "</b> has been updated with <b>new content</b>."
                                              , parse_mode=ParseMode.HTML.value)
                # post update not successful
                else:
                    self.context.send_message(chat_id
                                              , "Draft content could not be updated."
                                              , parse_mode=ParseMode.HTML.value)

                next_state = SelectDraftUpdateState(self.context, user_id, self.post_id, chat_id=chat_id)

            # previously selected post no longer exists
            else:
                self.context.send_message(chat_id
                                          , "It seems the draft you selected no longer exists..."
                                          , parse_mode=ParseMode.HTML.value)

                # show remaining drafts for updating
                user_drafts = self.context.get_user_posts(user_id=user_id, status=PostState.DRAFT)
                if len(user_drafts) > 0:
                    from packages.states.draft.updatedraftstate import UpdateDraftState
                    next_state = UpdateDraftState(self.context, user_id, chat_id=chat_id)
                # no remaining drafts -> automatically go back to main menu
                else:
                    from packages.states.navigation.idlestate import IdleState
                    next_state = IdleState(self.context, user_id, chat_id=chat_id)

        return next_state
