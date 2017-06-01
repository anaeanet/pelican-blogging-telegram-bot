from packages.bot.parsemode import ParseMode
from packages.states.navigation.selectdraftupdatestate import SelectDraftUpdateState

__author__ = "aneanet"


class SetTitleImageState(SelectDraftUpdateState):
    """
    Concrete state implementation.
    Lets the user select a title image from all image linked to the previously selected post.
    """

    @property
    def init_message(self):
        message = "It seems the draft you selected no longer exists..."

        user_drafts = self.context.get_posts(post_id=self.post_id)
        if len(user_drafts) > 0:
            post_title = user_drafts[0]["title"]
            message = "Which *image* do you want to set as *title image* of draft *" + post_title + "*?"

        return message

    @property
    def initial_options(self):
        reply_options = [{"text": "<< update options", "callback_data": "/selectupdate"}
                        , {"text": "<< drafts", "callback_data": "/updatedraft"}]

        # identify title image of post
        title_image_id = None
        user_drafts = self.context.get_posts(post_id=self.post_id)
        if len(user_drafts) > 0:
            title_image_id = user_drafts[0]["title_image"]

        # show select & preview button for every image currently assigned to draft, mark current title image
        for post_image in self.context.get_post_images(post_id=self.post_id):
            button_title = post_image["file_name"]

            # mark title image
            if title_image_id is not None and post_image["post_image_id"] == title_image_id:
                button_title += " - TITLE"

            reply_options.append({"text": button_title, "callback_data": "/settitleimage " + str(post_image["post_image_id"])})
            reply_options.append({"text": "preview", "callback_data": "/previewpostimage " + str(post_image["post_image_id"])})

        reply_options.append({"text": "<< main menu", "callback_data": "/mainmenu"})

        return reply_options

    def process_callback_query(self, user_id, chat_id, message_id, data):
        command_array = data.split(" ")

        # TODO cleanup

        # only accept "/settitleimage ..." callback queries, have super() handle everything else
        if len(command_array) > 1 and command_array[0] == "/settitleimage":

            # post_image selected as title image - /settitleimage <post_image_id>
            if len(command_array) == 2:
                post_image_id = command_array[1]

                user_drafts = self.context.get_posts(post_id=self.post_id)
                if len(user_drafts) > 0:
                    post_title = user_drafts[0]["title"]

                    post_images = self.context.get_post_images(post_image_id=post_image_id)
                    if len(post_images) > 0:
                        post_image_name = post_images[0]["file_name"]

                        # set selected image as title image of post
                        self.context.update_post(self.post_id, title_image=post_image_id)

                        self.context.edit_message_text(chat_id, message_id
                                                       , "Selected image *" + post_image_name + "* as title image for draft *" + post_title + "*."
                                                       , parse_mode=ParseMode.MARKDOWN.value)

                    else:
                        self.context.edit_message_text(chat_id, self.message_id
                                                       , "It seems the image you selected no longer exists..."
                                                       , parse_mode=ParseMode.MARKDOWN.value)

                    # after setting title image (successful or not), go back to update option menu for selected draft
                    next_state = SelectDraftUpdateState(self.context, user_id, self.post_id, chat_id=chat_id)

                else:
                    self.context.edit_message_text(chat_id, self.message_id
                                                   , "It seems the draft you selected no longer exists..."
                                                   , parse_mode=ParseMode.MARKDOWN.value)

                    # show remaining drafts for deletion
                    if len(self.context.get_posts(user_id=user_id, status="draft")) > 0:
                        from packages.states.draft.deletedraftstate import DeleteDraftState
                        next_state = DeleteDraftState(self.context, user_id, chat_id=chat_id)
                    # no remaining drafts -> automatically go back to main menu
                    else:
                        from packages.states.navigation.idlestate import IdleState
                        next_state = IdleState(self.context, user_id, chat_id=chat_id)

                self.context.set_user_state(user_id, next_state)

        # only accept "/previewpostimage ..." callback queries, have super() handle everything else
        elif len(command_array) > 1 and command_array[0] == "/previewpostimage":

            # post_image selected for preview - /previewpostimage <post_image_id>
            if len(command_array) == 2:
                post_image_id = command_array[1]

                # remove inline keyboard from latest bot message (by leaving out reply_options parameter)
                self.build_state_message(chat_id, self.init_message, message_id=self.message_id)

                user_drafts = self.context.get_posts(post_id=self.post_id)
                if len(user_drafts) > 0:

                    post_images = self.context.get_post_images(post_image_id=post_image_id)
                    if len(post_images) > 0:
                        post_image = post_images[0]
                        thumb_id = post_image["thumb_id"]
                        file_id = post_image["file_id"]
                        file_name = post_image["file_name"]
                        caption = post_image["caption"]

                        # build caption from file_name and actual caption - if one was provided
                        image_caption = file_name
                        if caption:
                            image_caption += "\r\n" + caption
                        if len(image_caption) > 100:
                            image_caption = image_caption[:min(100, len(image_caption)-1)] + "..."

                        # send thumbnail, or original photo if no thumbnail exists
                        self.context.send_photo(chat_id, thumb_id if thumb_id else file_id, caption=image_caption)

                    else:
                        self.context.edit_message_text(chat_id, self.message_id
                                                       , "It seems the image you selected no longer exists..."
                                                       , parse_mode=ParseMode.MARKDOWN.value)

                    # show remaining images for deletion
                    if len(self.context.get_post_images(post_id=self.post_id)) > 0:
                        next_state = SetTitleImageState(self.context, user_id, self.post_id, chat_id=chat_id)
                    # no remaining images -> automatically go back to update option menu
                    else:
                        next_state = SelectDraftUpdateState(self.context, user_id, self.post_id, chat_id=chat_id)

                else:
                    self.context.edit_message_text(chat_id, self.message_id
                                                   , "It seems the draft you selected no longer exists..."
                                                   , parse_mode=ParseMode.MARKDOWN.value)

                    # show remaining drafts for deletion
                    if len(self.context.get_posts(user_id=user_id, status="draft")) > 0:
                        from packages.states.draft.deletedraftstate import DeleteDraftState
                        next_state = DeleteDraftState(self.context, user_id, chat_id=chat_id)
                    # no remaining drafts -> automatically go back to main menu
                    else:
                        from packages.states.navigation.idlestate import IdleState
                        next_state = IdleState(self.context, user_id, chat_id=chat_id)

                self.context.set_user_state(user_id, next_state)

        else:
            super().process_callback_query(user_id, chat_id, message_id, data)