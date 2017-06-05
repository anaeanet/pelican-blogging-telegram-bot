import re

from packages.bot.parsemode import ParseMode
from packages.states.navigation.selectdraftupdatestate import SelectDraftUpdateState
from packages.datamodel.poststate import PostState

__author__ = "aneanet"


class AddTagState(SelectDraftUpdateState):
    """
    Concrete state implementation.

    Accepts plain text message as new tag(s) of draft/post.
    """

    @property
    def welcome_message(self):
        message = "It seems the draft you selected no longer exists..."

        post = self.context.get_post(self.post_id)
        if post is not None:
            message = "What <b>tag(s)</b> do you want to add to draft <b>" + post.title + "</b>? " \
                        + "Comma-separate multiple tags."

            # add current post_tags to init_message
            if len(post.tags) > 0:
                message += "\r\n\r\n" + "<b>Current tag(s)</b>" \
                           + "\r\n" + ", ".join([tag.name for tag in post.tags])

        return message

    @property
    def callback_options(self):
        # add buttons to return to update option menu, draft list, or main menu
        return [{"text": "<< update options", "callback_data": "/selectupdate"}
                , {"text": "<< drafts", "callback_data": "/updatedraft"}
                , {"text": "<< main menu", "callback_data": "/mainmenu"}]

    def process_message(self, user_id, chat_id, text, entities):
        next_state = self
        text = text.strip(' \t\n\r')

        # let super() handle any bot commands
        if text.startswith("/") or "bot_command" in [entity["type"] for entity in entities]:
            next_state = super().process_message(user_id, chat_id, text, entities)

        # accept simple text as tag list
        else:
            # remove inline keyboard from latest bot message (by leaving out reply_options parameter)
            self.build_state_message(chat_id, self.welcome_message, message_id=self.message_id)

            # check if previously selected post still exists
            post = self.context.get_post(self.post_id)
            if post is not None:

                new_tags = []
                for new_tag in [x.strip(' \t\n\r') for x in re.split("[,\t\n\r]", text)]:

                    # ignore "empty" tags
                    if len(new_tag) == 0:
                        continue

                    tag = self.context.add_post_tag(post.id, new_tag)
                    if tag is not None:
                        new_tags.append(tag.name)

                if len(new_tags) > 0:
                    self.context.send_message(chat_id
                                              , "Tag(s) <b>" + ", ".join(new_tags) + "</b> have been added to draft <b>" + post.title + "</b>."
                                              , parse_mode=ParseMode.HTML.value)
                else:
                    self.context.send_message(chat_id
                                              , "<b>No tags(s) added</b>. All specified tag(s) were already assigned to draft <b>" + post.title + "</b>."
                                              , parse_mode=ParseMode.HTML.value)

                next_state = AddTagState(self.context, user_id, self.post_id, chat_id=chat_id)

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
