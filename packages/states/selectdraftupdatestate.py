from packages.states.abstractuserpoststate import AbstractUserPostState
from packages.states.idlestate import IdleState
from packages.bot.parsemode import ParseMode

__author__ = "aneanet"


class SelectDraftUpdateState(AbstractUserPostState, IdleState):
    """
    Concrete state implementation.
    Lets the user select what to change on a previously chosen draft.
    """

    @property
    def init_message(self):
        message = "It seems the draft you selected no longer exists..."
        user_drafts = self.context.get_posts(post_id=self.post_id)
        if len(user_drafts) > 0:
            post_title = user_drafts[0]["title"]
            message = "What do you want to do with draft *" + post_title + "*?"
        return message

    @property
    def initial_options(self):
        reply_options = [{"text": "<< drafts", "callback_data": "/updatedraft"}]

        user_drafts = self.context.get_posts(post_id=self.post_id)
        if len(user_drafts) > 0:
            reply_options.append({"text": "EDIT content", "callback_data": "/selectupdate /editcontent"})

            reply_options.append({"text": "ADD tag(s)", "callback_data": "/selectupdate /addtag"})
            # only show option to delete tags if post already has tags
            if len(self.context.get_post_tags(post_id=self.post_id)) > 0:
                reply_options.append({"text": "DELETE tag(s)", "callback_data": "/selectupdate /deletetag"})
            else:
                reply_options.append([])

            reply_options.append({"text": "ADD image(s)", "callback_data": "/selectupdate /addimage"})
            # only show option to delete images if post already has images
            if len(self.context.get_post_images(post_id=self.post_id)) > 0:
                reply_options.append({"text": "DELETE image(s)", "callback_data": "/selectupdate /deleteimage"})
            else:
                reply_options.append([])

            reply_options.append({"text": "SET title image", "callback_data": "/selectupdate /settitleimage"})
            # only show option to delete title image if post already has a title image
            user_posts = self.context.get_posts(post_id=self.post_id)
            if len(user_posts) > 0 and user_posts[0]["title_image"] is not None:
                reply_options.append({"text": "DELETE title image", "callback_data": "/selectupdate /deletetitleimage"})
            else:
                reply_options.append([])

        reply_options.append({"text": "<< main menu", "callback_data": "/mainmenu"})
        return reply_options

    def process_callback_query(self, user_id, chat_id, message_id, data):
        command_array = data.split(" ")

        # only accept "/selectupdate ..." callback query from any selected update option state
        if len(command_array) == 1:
            if command_array[0] == "/selectupdate":
                next_state = SelectDraftUpdateState(self.context, user_id, self.post_id, chat_id=chat_id, message_id=message_id)
                self.context.set_user_state(user_id, next_state)

        # only accept "/selectupdate ..." callback queries, have super() handle everything else
        if len(command_array) > 1 and command_array[0] == "/selectupdate":

            # update-option was chosen for selected draft - /selectupdate <update-option>
            if len(command_array) == 2:

                # user attempts to update the selected draft's content
                if command_array[1] == "/editcontent":

                    user_drafts = self.context.get_posts(post_id=self.post_id,)
                    if len(user_drafts) > 0:
                        post_title = user_drafts[0]["title"]
                        post_content = user_drafts[0]["content"]

                        if post_content is not None and len(post_content) > 0:
                            self.context.edit_message_text(chat_id, self.message_id
                                                      , "Draft *" + post_title + "* currently has the following content:"
                                                      , parse_mode=ParseMode.MARKDOWN.value)
                            self.context.send_message(chat_id
                                                      , post_content)
                            from packages.states.editcontentstate import EditContentState
                            next_state = EditContentState(self.context, user_id, self.post_id, chat_id=chat_id)

                        else:
                            from packages.states.editcontentstate import EditContentState
                            next_state = EditContentState(self.context, user_id, self.post_id, chat_id=chat_id, message_id=self.message_id)

                    else:
                        self.context.edit_message_text(chat_id, self.message_id
                                                  , "It seems the draft you selected no longer exists..."
                                                  , parse_mode=ParseMode.MARKDOWN.value)

                        # show remaining drafts for updating
                        if len(self.context.get_posts(user_id=user_id, status="draft")) > 0:
                            from packages.states.updatedraftstate import UpdateDraftState
                            next_state = UpdateDraftState(self.context, user_id, chat_id=chat_id)
                        # no remaining drafts -> automatically go back to main menu
                        else:
                            next_state = IdleState(self.context, user_id, chat_id=chat_id)

                    self.context.set_user_state(user_id, next_state)

                elif command_array[1] == "/addtag":
                    from packages.states.addtagstate import AddTagState
                    next_state = AddTagState(self.context, user_id, self.post_id, chat_id=chat_id, message_id=self.message_id)
                    self.context.set_user_state(user_id, next_state)
                elif command_array[1] == "/deletetag":
                    from packages.states.deletetagstate import DeleteTagState
                    next_state = DeleteTagState(self.context, user_id, self.post_id, chat_id=chat_id, message_id=self.message_id)
                    self.context.set_user_state(user_id, next_state)
                elif command_array[1] == "/addimage":
                    from packages.states.addimagestate import AddImageState
                    next_state = AddImageState(self.context, user_id, self.post_id, chat_id=chat_id, message_id=self.message_id)
                    self.context.set_user_state(user_id, next_state)
                elif command_array[1] == "/deleteimage":
                    # TODO
                    None
                elif command_array[1] == "/settitleimage":
                    # TODO
                    None
                elif command_array[1] == "/deletetitleimage":
                    # TODO
                    None

        else:
            super().process_callback_query(user_id, chat_id, message_id, data)
