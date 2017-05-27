from packages.states.selectdraftupdatestate import SelectDraftUpdateState
from packages.bot.parsemode import ParseMode
import re

__author__ = "aneanet"


class AddTagState(SelectDraftUpdateState):
    """
    Concrete state implementation.
    Accepts plain text message as new tag(s) of draft/post.
    """

    @property
    def init_message(self):
        message = "It seems the draft you selected no longer exists..."

        user_drafts = self.context.get_posts(post_id=self.post_id, user_id=self.user_id)
        if len(user_drafts) > 0:
            post_title = user_drafts[0]["title"]
            message = "What tag(s) do you want to add to draft *" + post_title + "*? " \
                      + "(comma-separate multiple tags)"

            # add current post_tags to init_messaage
            current_tags = self.context.get_post_tag(self.post_id)
            if len(current_tags) > 0:
                message += "\r\n\r\n" + "*Current tags*\r\n" + ", ".join([tag["name"] for tag in current_tags])

        return message

    @property
    def initial_options(self):
        reply_options = [{"text": "<< update options", "callback_data": "/selectupdate"}
                         # TODO add button to show existing tags of user
                        , {"text": "<< drafts", "callback_data": "/updatedraft"}
                        , {"text": "<< main menu", "callback_data": "/mainmenu"}]
        return reply_options

    def process_message(self, user_id, chat_id, text):
        if text.startswith("/"):
            super().process_message(user_id, chat_id, text)
        else:
            # remove inline keyboard from latest bot message (by leaving out reply_options parameter)
            self.build_state_message(chat_id, self.init_message, message_id=self.message_id)

            user_drafts = self.context.get_posts(post_id=self.post_id, user_id=self.user_id)
            if len(user_drafts) > 0:
                post_title = user_drafts[0]["title"]


                new_tags = []
                for tag in [x.strip(' \t\n\r') for x in re.split("[,\t\n\r]", text)]:

                    # make sure only new tags are added, i.e. existing ones are ignored
                    current_post_tags = self.context.get_post_tag(self.post_id, name=tag)
                    if tag not in current_post_tags:
                        new_tags.append(tag.strip(' \t\n\r'))
                        self.context.add_post_tag(self.post_id, tag)

                self.context.send_message(chat_id
                                          , "Tag(s) *" + ", ".join(new_tags) + "* successfully added to draft *" + post_title + "*."
                                          , parse_mode=ParseMode.MARKDOWN.value)

                next_state = SelectDraftUpdateState(self.context, user_id, self.post_id, chat_id=chat_id)

            else:
                self.context.send_message(chat_id
                                          , "It seems the draft you selected no longer exists..."
                                          , parse_mode=ParseMode.MARKDOWN.value)

                # show remaining drafts for updating
                if len(self.context.get_posts(user_id=user_id, status="draft")) > 0:
                    from packages.states.updatedraftstate import UpdateDraftState
                    next_state = UpdateDraftState(self.context, user_id, chat_id=chat_id)
                # no remaining drafts -> automatically go back to main menu
                else:
                    from packages.states.idlestate import IdleState
                    next_state = IdleState(self.context, user_id, chat_id=chat_id)

            self.context.set_user_state(user_id, next_state)
