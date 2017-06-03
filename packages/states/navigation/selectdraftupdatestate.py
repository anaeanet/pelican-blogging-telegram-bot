from packages.bot.parsemode import ParseMode
from packages.states.abstract.abstractuserpoststate import AbstractUserPostState
from packages.states.navigation.idlestate import IdleState

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
            message = "What do you want to do with draft <b>" + post_title + "</b>?"
        return message

    @property
    def initial_options(self):
        reply_options = [{"text": "<< drafts", "callback_data": "/updatedraft"}, []]

        user_drafts = self.context.get_posts(post_id=self.post_id)
        if len(user_drafts) > 0:
            post = user_drafts[0]

            reply_options.append({"text": "EDIT title", "callback_data": "/selectupdate /edittitle"})
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

            # only show option to set title image if post already has at least one image
            if len(self.context.get_post_images(post_id=self.post_id)) > 0:
                reply_options.append({"text": "SET title image", "callback_data": "/selectupdate /settitleimage"})
            # only show option to delete title image if post already has a title image
            user_posts = self.context.get_posts(post_id=self.post_id)
            if len(user_posts) > 0 and user_posts[0]["title_image"] is not None:
                reply_options.append({"text": "DELETE title image", "callback_data": "/selectupdate /deletetitleimage"})
            else:
                reply_options.append([])

            # only show option to update gallery title if there is at least on non-title image
            post_images = self.context.get_post_images(post_id=self.post_id)
            if len(post_images) > 1 or (len(post_images) == 1 and post_images[0]["post_image_id"] != post["title_image"]):
                reply_options.append({"text": "EDIT gallery title", "callback_data": "/selectupdate /editgallerytitle"})
                reply_options.append([])

        reply_options.append({"text": "<< main menu", "callback_data": "/mainmenu"})
        return reply_options

    def process_callback_query(self, user_id, chat_id, message_id, data):
        command_array = data.split(" ")

        # only accept "/selectupdate ..." callback query from any selected update option state
        if len(command_array) == 1:
            if command_array[0] == "/selectupdate":
                next_state = SelectDraftUpdateState(self.context, user_id, self.post_id, chat_id=chat_id, message_id=message_id)
                self.context.set_state(user_id, next_state)

        # only accept "/selectupdate ..." callback queries, have super() handle everything else
        if len(command_array) > 1 and command_array[0] == "/selectupdate":

            # update-option was chosen for selected draft - /selectupdate <update-option>
            if len(command_array) == 2:
                next_state = self

                # user attempts to update the selected draft's content
                if command_array[1] == "/edittitle":
                    from packages.states.draft.editdrafttitlestate import EditDraftTitleState
                    next_state = EditDraftTitleState(self.context, user_id, self.post_id, chat_id=chat_id, message_id=self.message_id)
                elif command_array[1] == "/editcontent":
                    from packages.states.draft.editcontentstate import EditContentState
                    next_state = EditContentState(self.context, user_id, self.post_id, chat_id=chat_id, message_id=self.message_id)
                elif command_array[1] == "/addtag":
                    from packages.states.tag.addtagstate import AddTagState
                    next_state = AddTagState(self.context, user_id, self.post_id, chat_id=chat_id, message_id=self.message_id)
                elif command_array[1] == "/deletetag":
                    from packages.states.tag.deletetagstate import DeleteTagState
                    next_state = DeleteTagState(self.context, user_id, self.post_id, chat_id=chat_id, message_id=self.message_id)
                elif command_array[1] == "/addimage":
                    from packages.states.image.addimagestate import AddImageState
                    next_state = AddImageState(self.context, user_id, self.post_id, chat_id=chat_id, message_id=self.message_id)
                elif command_array[1] == "/deleteimage":
                    from packages.states.image.deleteimagestate import DeleteImageState
                    next_state = DeleteImageState(self.context, user_id, self.post_id, chat_id=chat_id, message_id=self.message_id)
                elif command_array[1] == "/settitleimage":
                    from packages.states.image.settitleimagestate import SetTitleImageState
                    next_state = SetTitleImageState(self.context, user_id, self.post_id, chat_id=chat_id, message_id=self.message_id)
                elif command_array[1] == "/deletetitleimage":
                    from packages.states.image.deletetitleimagestate import DeleteTitleImageState
                    next_state = DeleteTitleImageState(self.context, user_id, self.post_id, chat_id=chat_id, message_id=self.message_id)
                elif command_array[1] == "/editgallerytitle":
                    from packages.states.image.editgallerytitlestate import EditGalleryTitleState
                    next_state = EditGalleryTitleState(self.context, user_id, self.post_id, chat_id=chat_id, message_id=self.message_id)

                self.context.set_state(user_id, next_state)

        else:
            super().process_callback_query(user_id, chat_id, message_id, data)
