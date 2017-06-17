from packages.bot.parsemode import ParseMode
from packages.states.abstract.abstractuserpoststate import AbstractUserPostState
from packages.states.navigation.idlestate import IdleState

__author__ = "aneanet"


class SelectDraftUpdateState(AbstractUserPostState, IdleState):
    """
    Concrete state implementation.

    Lets the user select what attributes to change on a previously chosen draft.
    """

    @property
    def welcome_message(self):
        message = "It seems the draft you selected no longer exists..."

        post = self.bot.persistence.get_post(self.post_id)
        if post is not None:
            message = "What do you want to do with draft <b>" + post.title + "</b>?"

        return message

    @property
    def callback_options(self):

        # add button to return to draft list
        reply_options = [{"text": "<< drafts", "callback_data": "/updatedraft"}, []]

        # show update options only if previously selected post still exists
        post = self.bot.persistence.get_post(self.post_id)
        if post is not None:

            reply_options.append({"text": "EDIT title", "callback_data": "/selectupdate /edittitle"})
            reply_options.append({"text": "EDIT content", "callback_data": "/selectupdate /editcontent"})

            # --- tag buttons ---

            reply_options.append({"text": "ADD tag(s)", "callback_data": "/selectupdate /addtag"})

            # only show option to delete tags if post already has tags
            if len(post.tags) > 0:
                reply_options.append({"text": "DELETE tag(s)", "callback_data": "/selectupdate /deletetag"})
            else:
                reply_options.append([])

            # --- image buttons ---

            reply_options.append({"text": "ADD image(s)", "callback_data": "/selectupdate /addimage"})

            # only show option to delete images if post already has images
            if len(post.gallery.images) > 0 or post.title_image is not None:
                reply_options.append({"text": "DELETE image(s)", "callback_data": "/selectupdate /deleteimage"})
            else:
                reply_options.append([])

            # --- title image buttons ---

            # only show option to set title image if post already has at least one non-title image
            if len(post.gallery.images) > 0:
                reply_options.append({"text": "SET title image", "callback_data": "/selectupdate /settitleimage"})

            # only show option to delete title image if post already has a title image
            if post.title_image is not None:
                reply_options.append({"text": "DELETE title image", "callback_data": "/selectupdate /deletetitleimage"})
            else:
                reply_options.append([])

            # force line break in inline keyboard if there is an odd number of reply_options
            if len(reply_options) % 2 == 1:
                reply_options.append([])

            # --- gallery title button ---

            # only show option to update gallery title if there is at least one non-title image
            if len(post.gallery.images) > 0:
                reply_options.append({"text": "EDIT gallery title", "callback_data": "/selectupdate /editgallerytitle"})
                reply_options.append([])

            # --- publish button ---

            if len(post.title) > 0 and len(post.content) > 0:
                reply_options.append({"text": "PUBLISH", "callback_data": "/selectupdate /publish"})
                reply_options.append([])

        # add button to return to main menu
        reply_options.append({"text": "<< main menu", "callback_data": "/mainmenu"})

        return reply_options

    def process_callback_query(self, user_id, chat_id, message_id, data):
        next_state = self
        command_array = data.split(" ")

        # accept "/selectupdate" callback query -> serves as global return command to show update options menu
        if len(command_array) == 1 and command_array[0] == "/selectupdate":
            next_state = SelectDraftUpdateState(self.bot, user_id, self.post_id, chat_id=chat_id, message_id=message_id)

        # only accept "/selectupdate <update_option>" callback queries
        elif len(command_array) == 2 and command_array[0] == "/selectupdate":

            # user attempts to update the selected draft's content
            if command_array[1] == "/edittitle":
                from packages.states.draft.editdrafttitlestate import EditDraftTitleState
                next_state = EditDraftTitleState(self.bot, user_id, self.post_id, chat_id=chat_id, message_id=self.message_id)
            elif command_array[1] == "/editcontent":
                from packages.states.draft.editdraftcontentstate import EditDraftContentState
                next_state = EditDraftContentState(self.bot, user_id, self.post_id, chat_id=chat_id, message_id=self.message_id)
            elif command_array[1] == "/addtag":
                from packages.states.tag.addtagstate import AddTagState
                next_state = AddTagState(self.bot, user_id, self.post_id, chat_id=chat_id, message_id=self.message_id)
            elif command_array[1] == "/deletetag":
                from packages.states.tag.deletetagstate import DeleteTagState
                next_state = DeleteTagState(self.bot, user_id, self.post_id, chat_id=chat_id, message_id=self.message_id)
            elif command_array[1] == "/addimage":
                from packages.states.image.addimagestate import AddImageState
                next_state = AddImageState(self.bot, user_id, self.post_id, chat_id=chat_id, message_id=self.message_id)
            elif command_array[1] == "/deleteimage":
                from packages.states.image.deleteimagestate import DeleteImageState
                next_state = DeleteImageState(self.bot, user_id, self.post_id, chat_id=chat_id, message_id=self.message_id)
            elif command_array[1] == "/settitleimage":
                from packages.states.image.settitleimagestate import SetTitleImageState
                next_state = SetTitleImageState(self.bot, user_id, self.post_id, chat_id=chat_id, message_id=self.message_id)
            elif command_array[1] == "/deletetitleimage":
                from packages.states.image.deletetitleimagestate import DeleteTitleImageState
                next_state = DeleteTitleImageState(self.bot, user_id, self.post_id, chat_id=chat_id, message_id=self.message_id)
            elif command_array[1] == "/editgallerytitle":
                from packages.states.image.editgallerytitlestate import EditGalleryTitleState
                next_state = EditGalleryTitleState(self.bot, user_id, self.post_id, chat_id=chat_id, message_id=self.message_id)
            elif command_array[1] == "/publish":
                from packages.states.draft.publishdraftstate import PublishDraftState
                next_state = PublishDraftState(self.bot, user_id, self.post_id, chat_id=chat_id, message_id=self.message_id)

        else:
            next_state = super().process_callback_query(user_id, chat_id, message_id, data)

        return next_state
