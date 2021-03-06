from packages.bot.parsemode import ParseMode
from packages.states.abstract.abstractuserstate import AbstractUserState
from packages.datamodel.poststate import PostState

__author__ = "aneanet"


class IdleState(AbstractUserState):
    """
    Concrete state implementation.

    This class serves as start state for all users of "PelicanMarkdownBot" 
    and provides functionality to process common commands and navigation.
    """

    @property
    def welcome_message(self):
        return "What do you want to do?"

    @property
    def callback_options(self):

        # show optin to create new draft from scratch
        reply_options = [{"text": "CREATE a draft", "callback_data": "/createdraft"}]

        user_posts = self.bot.persistence.get_posts(user_id=self.user_id)

        # if user already has any draft posts, show buttons to update or delete them
        user_drafts = [post for post in user_posts if post.status == PostState.DRAFT]
        if len(user_drafts) > 0:
            reply_options.append({"text": "UPDATE a draft", "callback_data": "/updatedraft"})
            reply_options.append({"text": "DELETE a draft", "callback_data": "/deletedraft"})

        # show update/delete options for previously published posts that do not have a follow-up draft or post
        published_posts = [post for post in user_posts if post.status == PostState.PUBLISHED]
        derived_posts = [post for post in user_posts if post.original_post is not None]
        if len(published_posts) > len(derived_posts):
            reply_options.append({"text": "UPDATE published post", "callback_data": "/updatepost"})
            reply_options.append({"text": "DELETE published post", "callback_data": "/deletepost"})

        return reply_options

    def process_message(self, user_id, chat_id, text, entities):

        # global commands
        if text in ["/start"]:

            # delete previous bot message (if existing) before sending new ones
            if self.message_id is not None:
                result = self.bot.delete_message(chat_id, self.message_id)
                # edit message instead if deletion does not work due to message being too old
                if False in result.values():
                    self.bot.edit_message_text(chat_id, self.message_id, "Message/Command not recognized!")

            self.bot.send_message(chat_id
                                  , "Welcome to your mobile blogging bot!"
                                  + "\r\n\r\n"
                                  + "I am here to help you create new blog posts or manage existing ones. "
                                  + "Just follow the interactive menu!"
                                  , parse_mode=ParseMode.HTML.value)
            next_state = IdleState(self.bot, user_id, chat_id=chat_id)

        else:
            next_state = self.process_unknown_update(chat_id)

        return next_state

    def process_photo_message(self, user_id, chat_id, file_id, thumb_id=None, caption=None):
        return self.process_unknown_update(chat_id)

    def process_callback_query(self, user_id, chat_id, message_id, data):
        next_state = self
        command_array = data.split(" ")

        if len(command_array) == 1:

            if command_array[0] == "/mainmenu":
                next_state = IdleState(self.bot, user_id, chat_id=chat_id, message_id=message_id)
            elif command_array[0] == "/createdraft":
                from packages.states.draft.createdraftstate import CreateDraftState
                next_state = CreateDraftState(self.bot, user_id, chat_id=chat_id, message_id=message_id)
            elif command_array[0] == "/updatedraft":
                from packages.states.draft.updatedraftstate import UpdateDraftState
                next_state = UpdateDraftState(self.bot, user_id, chat_id=chat_id, message_id=message_id)
            elif command_array[0] == "/deletedraft":
                from packages.states.draft.deletedraftstate import DeleteDraftState
                next_state = DeleteDraftState(self.bot, user_id, chat_id=chat_id, message_id=message_id)
            elif command_array[0] == "/updatepost":
                from packages.states.post.updatepoststate import UpdatePostState
                next_state = UpdatePostState(self.bot, user_id, chat_id=chat_id, message_id=message_id)
            elif command_array[0] == "/deletepost":
                from packages.states.post.deletepoststate import DeletePostState
                next_state = DeletePostState(self.bot, user_id, chat_id=chat_id, message_id=message_id)

        return next_state
