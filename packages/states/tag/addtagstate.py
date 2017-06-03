import re

from packages.bot.parsemode import ParseMode
from packages.states.navigation.selectdraftupdatestate import SelectDraftUpdateState

__author__ = "aneanet"


class AddTagState(SelectDraftUpdateState):
    """
    Concrete state implementation.
    Accepts plain text message as new tag(s) of draft/post.
    """

    @property
    def welcome_message(self):
        message = "It seems the draft you selected no longer exists..."

        user_drafts = self.context.get_posts(post_id=self.post_id)
        if len(user_drafts) > 0:
            post_title = user_drafts[0]["title"]
            message = "What <b>tag(s)</b> do you want to add to draft <b>" + post_title + "</b>? " \
                        + "Comma-separate multiple tags."

            # add current post_tags to init_message
            tags = []
            post_tags = self.context.get_post_tags(post_id=self.post_id)
            for post_tag in post_tags:
                tag_id = post_tag["tag_id"]
                for tag in self.context.get_tags(tag_id=tag_id):
                    tags.append(tag["name"])

            if len(tags) > 0:
                message += "\r\n\r\n" + "<b>Current tag(s)</b>\r\n" + ", ".join(tags)

        return message

    @property
    def callback_options(self):
        reply_options = [{"text": "<< update options", "callback_data": "/selectupdate"}
                        , {"text": "<< drafts", "callback_data": "/updatedraft"}
                        , {"text": "<< main menu", "callback_data": "/mainmenu"}]
        return reply_options

    def process_message(self, user_id, chat_id, text, entities):
        if text.startswith("/"):
            super().process_message(user_id, chat_id, text)
        else:
            # remove inline keyboard from latest bot message (by leaving out reply_options parameter)
            self.build_state_message(chat_id, self.welcome_message, message_id=self.message_id)

            user_drafts = self.context.get_posts(post_id=self.post_id)
            if len(user_drafts) > 0:
                post_title = user_drafts[0]["title"]

                new_tag_names = []
                for new_tag_name in [x.strip(' \t\n\r') for x in re.split("[,\t\n\r]", text)]:

                    # ignore "empty" tags
                    if len(new_tag_name) == 0:
                        continue

                    # add tag if it does not exist yet
                    tags = self.context.get_tags(name=new_tag_name)
                    if new_tag_name not in [tag["name"] for tag in tags]:
                        self.context.add_tag(new_tag_name)

                    # fetch newly added tag
                    tags = self.context.get_tags(name=new_tag_name)
                    if len(tags) > 0:
                        tag_id = tags[0]["tag_id"]

                        # if post does not have tag yet, add it
                        post_tags = self.context.get_post_tags(post_id=self.post_id, tag_id=tag_id)
                        if len(post_tags) == 0:
                            self.context.add_post_tag(self.post_id, tag_id)
                            new_tag_names.append(new_tag_name)

                if len(new_tag_names) > 0:
                    self.context.send_message(chat_id
                                              , "Tag(s) <b>" + ", ".join(new_tag_names) + "</b> have been added to draft <b>" + post_title + "</b>."
                                              , parse_mode=ParseMode.HTML.value)
                else:
                    self.context.send_message(chat_id
                                              , "<b>No tags(s) added</b>. All specified tag(s) were already assigned to draft <b>" + post_title + "</b>."
                                              , parse_mode=ParseMode.HTML.value)

                next_state = AddTagState(self.context, user_id, self.post_id, chat_id=chat_id)

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
