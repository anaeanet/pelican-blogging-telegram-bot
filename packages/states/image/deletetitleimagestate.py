from packages.bot.parsemode import ParseMode
from packages.states.navigation.selectdraftupdatestate import SelectDraftUpdateState
from packages.datamodel.poststate import PostState

__author__ = "aneanet"


class DeleteTitleImageState(SelectDraftUpdateState):
    """
    Concrete state implementation.

    Lets the user remove a title image from the previously selected post.
    """

    @property
    def welcome_message(self):
        message = "It seems the draft you selected no longer exists..."

        post = self.context.persistence.get_post(self.post_id)
        if post is not None and post.title_image is not None:
            message = "Do you <b>really</b> want to <b>remove " + post.title_image.name + "</b> as title image of draft <b>" + post.title + "</b>?"

        return message

    @property
    def callback_options(self):
        # add buttons to return to update option menu, draft list
        reply_options = [{"text": "<< update options", "callback_data": "/selectupdate"}
                        , {"text": "<< drafts", "callback_data": "/updatedraft"}]

        # show confirm deletion and preview button
        post = self.context.persistence.get_post(self.post_id)
        if post is not None and post.title_image is not None:
            reply_options.append({"text": "YES, delete", "callback_data": "/deletetitleimage " + str(post.title_image.id)})
            reply_options.append({"text": "preview", "callback_data": "/previewpostimage " + str(post.title_image.id)})

        # add button to return to main menu
        reply_options.append({"text": "<< main menu", "callback_data": "/mainmenu"})

        return reply_options

    def process_callback_query(self, user_id, chat_id, message_id, data):
        next_state = self
        command_array = data.split(" ")

        # only accept "/deletetitleimage <image_id>" callback queries
        if len(command_array) == 2 and command_array[0] == "/deletetitleimage":

            image_id = command_array[1]

            # check if previously selected post still exists
            post = self.context.persistence.get_post(self.post_id)
            if post is not None:

                removed_image = post.title_image
                updated_post = self.context.persistence.update_post(post.id, post.user.id, post.title, post.status
                                                                    , post.gallery.title
                                                                    , post.content
                                                                    , None
                                                                    , post.tmsp_publish
                                                                    , None if post.original_post is None else post.original_post.id)

                if updated_post is not None:
                    self.context.edit_message_text(chat_id, message_id
                                                   , "Image <b>" + removed_image.name + "</b> has been <b>deleted as title image</b> from draft <b>" + post.title + "</b>."
                                                   , parse_mode=ParseMode.HTML.value)

                else:
                    self.context.edit_message_text(chat_id, self.message_id
                                                   , "It seems the image you selected no longer exists..."
                                                   , parse_mode=ParseMode.HTML.value)

                # after deleting title image (successful or not), go back to update option menu for selected draft
                next_state = SelectDraftUpdateState(self.context, user_id, self.post_id, chat_id=chat_id)

            # previously selected post no longer exists
            else:
                self.context.send_message(chat_id
                                          , "It seems the draft you selected no longer exists..."
                                          , parse_mode=ParseMode.HTML.value)

                # show remaining drafts for updating
                user_drafts = self.context.persistence.get_posts(user_id=user_id, status=PostState.DRAFT)
                if len(user_drafts) > 0:
                    from packages.states.draft.updatedraftstate import DeleteDraftState
                    next_state = DeleteDraftState(self.context, user_id, chat_id=chat_id)
                # no remaining drafts -> automatically go back to main menu
                else:
                    from packages.states.navigation.idlestate import IdleState
                    next_state = IdleState(self.context, user_id, chat_id=chat_id)

        # only accept "/previewpostimage <image_id>" callback queries
        elif len(command_array) == 2 and command_array[0] == "/previewpostimage":

            image_id = command_array[1]

            # remove inline keyboard from latest bot message (by leaving out reply_options parameter)
            self.build_state_message(chat_id, self.welcome_message, message_id=self.message_id)

            # check if previously selected post still exists
            post = self.context.persistence.get_post(self.post_id)
            if post is not None:

                preview_image = None
                for image in post.gallery.images + ([post.title_image] if post.title_image is not None else []):
                    # ignore "wrong" images
                    if str(image.id) != str(image_id):
                        continue
                    else:
                        preview_image = image

                # image found -> preview
                if image is not None:
                    self.context.send_photo(chat_id, image.thumb_id if image.thumb_id else image.file_id,
                                            caption=image.caption)
                # image not found
                else:
                    self.context.edit_message_text(chat_id, self.message_id
                                                   , "It seems the image you selected no longer exists..."
                                                   , parse_mode=ParseMode.HTML.value)

                next_state = DeleteTitleImageState(self.context, user_id, post.id, chat_id=chat_id)

            # previously selected post no longer exists
            else:
                self.context.send_message(chat_id
                                          , "It seems the draft you selected no longer exists..."
                                          , parse_mode=ParseMode.HTML.value)

                # show remaining drafts for updating
                user_drafts = self.context.persistence.get_posts(user_id=user_id, status=PostState.DRAFT)
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
