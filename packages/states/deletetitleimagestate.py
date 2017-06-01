from packages.states.selectdraftupdatestate import SelectDraftUpdateState
from packages.bot.parsemode import ParseMode

__author__ = "aneanet"


class DeleteTitleImageState(SelectDraftUpdateState):
    """
    Concrete state implementation.
    Lets the user remove a title image from the previously selected post.
    """

    @property
    def init_message(self):
        message = "It seems the draft you selected no longer exists..."

        user_drafts = self.context.get_posts(post_id=self.post_id)
        if len(user_drafts) > 0:
            post_title = user_drafts[0]["title"]
            title_image = user_drafts[0]["title_image"]

            post_images = self.context.get_post_images(post_image_id=title_image)
            if len(post_images) > 0:
                title_image_name = post_images[0]["file_name"]

                message = "Do you really want to remove *" + title_image_name + "* as title image of draft *" + post_title + "*?"

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

            reply_options.append({"text": "Yes, confirm", "callback_data": "/deletetitleimage " + str(title_image_id)})
            reply_options.append({"text": "preview", "callback_data": "/previewpostimage " + str(title_image_id)})

        reply_options.append({"text": "<< main menu", "callback_data": "/mainmenu"})

        return reply_options

    def process_callback_query(self, user_id, chat_id, message_id, data):
        command_array = data.split(" ")

        # TODO cleanup

        # only accept "/deletetitleimage ..." callback queries, have super() handle everything else
        if len(command_array) > 1 and command_array[0] == "/deletetitleimage":

            # post_image selected for deletion - /deletetitleimage <post_image_id>
            if len(command_array) == 2:
                post_image_id = command_array[1]

                user_drafts = self.context.get_posts(post_id=self.post_id)
                if len(user_drafts) > 0:
                    post_title = user_drafts[0]["title"]

                    post_images = self.context.get_post_images(post_image_id=post_image_id)
                    if len(post_images) > 0:
                        post_image_name = post_images[0]["file_name"]

                        # remove image from post
                        self.context.delete_title_image(self.post_id)

                        self.context.edit_message_text(chat_id, message_id
                                                       , "Successfully deleted image *" + post_image_name + "* as title image from draft *" + post_title + "*."
                                                       , parse_mode=ParseMode.MARKDOWN.value)

                    else:
                        self.context.edit_message_text(chat_id, self.message_id
                                                       , "It seems the image you selected no longer exists..."
                                                       , parse_mode=ParseMode.MARKDOWN.value)

                    # after deleting title image (successful or not), go back to update option menu for selected draft
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
                        next_state = DeleteTitleImageState(self.context, user_id, self.post_id, chat_id=chat_id)
                    # no remaining images -> automatically go back to update option menu
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
