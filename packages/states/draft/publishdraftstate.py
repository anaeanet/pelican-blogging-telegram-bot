import re

from packages.bot.parsemode import ParseMode
from packages.states.navigation.selectdraftupdatestate import SelectDraftUpdateState

__author__ = "aneanet"


class PublishDraftState(SelectDraftUpdateState):
    """
    Concrete state implementation.
    Accepts plain text message to publish a current draft either as draft post or final post.
    """

    # TODO

    @property
    def welcome_message(self):
        message = "It seems the draft you selected no longer exists..."

        user_drafts = self.context.get_posts(post_id=self.post_id)
        if len(user_drafts) > 0:
            post_title = user_drafts[0]["title"]
            message = "How do you want to <b>publish</b> draft <b>" + post_title + "</b>? Type one of the below options!" \
                      + "\r\n\r\n" + "<b>Publishing options</b>" \
                      + "\r\n" + "/publish draft" \
                      + "\r\n" + "/publish post"

        return message

    @property
    def callback_options(self):
        reply_options = [{"text": "<< update options", "callback_data": "/selectupdate"}
                        , {"text": "<< drafts", "callback_data": "/updatedraft"}
                        , {"text": "<< main menu", "callback_data": "/mainmenu"}]
        return reply_options

    def process_message(self, user_id, chat_id, text, entities):
        next_state = self

        text = text.strip(' \t\n\r')
        if text.startswith("/") and not text.startswith("/publish"):
            next_state = super().process_message(user_id, chat_id, text, entities)
        else:
            # remove inline keyboard from latest bot message (by leaving out reply_options parameter)
            self.build_state_message(chat_id, self.welcome_message, message_id=self.message_id)

            user_drafts = self.context.get_posts(post_id=self.post_id)
            if len(user_drafts) > 0:
                post_title = user_drafts[0]["title"]

                command_parts = [x.strip(' \t\n\r') for x in text.split(" ")]
                if len(command_parts) == 2 and command_parts[0] == "/publish" and command_parts[1] in ["draft", "post"]:
                    status = command_parts[1] if command_parts[1] == "draft" else "published"

                    from datetime import datetime
                    if self.context.publish_post(self.post_id, status, datetime.now()) > 0:
                        self.context.send_message(chat_id
                                                  , "Draft <b>" + post_title + "</b> has been <b>published as " + command_parts[1] + "</b>."
                                                  , parse_mode=ParseMode.HTML.value)
                        from packages.states.navigation.idlestate import IdleState
                        next_state = IdleState(self.context, user_id, chat_id=chat_id)
                    else:
                        self.context.send_message(chat_id
                                                  , "Draft <b>" + post_title + "</b> could not be published."
                                                  , parse_mode=ParseMode.HTML.value)
                        next_state = SelectDraftUpdateState(self.context, user_id, self.post_id, chat_id=chat_id)

                else:
                    self.context.send_message(chat_id
                                              , "Command not recognized."
                                              , parse_mode=ParseMode.HTML.value)
                    next_state = PublishDraftState(self.context, user_id, self.post_id, chat_id=chat_id)

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

        return next_state
