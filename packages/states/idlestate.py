from packages.states.abstractstate import AbstractState
from packages.bot.parsemode import ParseMode
import packages.bot.telegram as telegram

__author__ = "aneanet"


class IdleState(AbstractState):
    """
    Concrete state implementation.
    This class serves as start state for all users of "PelicanMarkdownBot".
    """

    def process_update(self, update):
        print(update)

        update_type = telegram.get_update_type(update)

        if update_type == "message":
            user_id = telegram.get_update_sender_id(update)
            chat_id = update[update_type]["chat"]["id"]
            text = update[update_type]["text"].strip(' \t\n\r') if "text" in update[update_type] else None

            if text:
                # text message

                if text in ["/start", "/help"]:
                    self.get_context().send_message(chat_id, "Welcome to your mobile blogging bot! I am here to help you create new blog posts or update existing ones while you are on the go.\r\n"
                                                    + "\r\n" + "You can control me by the following commands:\r\n"
                                                    + "\r\n" + "*Drafts - Unpublished blog posts*"
                                                    + "\r\n" + "/createdraft - begin a new draft"
                                                    + "\r\n" + "/updatedraft - continue working on a draft"
                                                    + "\r\n" + "/deletedraft - delete a draft"
                                                    , parse_mode=ParseMode.MARKDOWN.value)
                    return

                elif text == "/createdraft":
                    from packages.states.createdraftstate import CreateDraftState
                    self.get_context().set_user_state(user_id, CreateDraftState(self.get_context()))
                    self.get_context().send_message(chat_id, "Alright. What is the *title* of your new draft?"
                                                    , parse_mode=ParseMode.MARKDOWN.value)
                    return

                elif text == "/deletedraft":
                    from packages.states.deletedraftstate import DeleteDraftState
                    self.get_context().set_user_state(user_id, DeleteDraftState(self.get_context()))

                    user_drafts = []
                    for post in self.get_context().get_posts(user_id=user_id, status="draft"):
                        user_drafts.append(post["title"])

                    if len(user_drafts) > 0:
                        self.get_context().send_message(chat_id, "Which draft do you want to delete?"
                                                    , parse_mode=ParseMode.MARKDOWN.value
                                                    , reply_markup=telegram.build_keyboard(user_drafts))
                    else:
                        self.get_context().send_message(chat_id, "I am sorry, but you don't have any drafts left."
                                                    , parse_mode=ParseMode.MARKDOWN.value)
                    return

            self.get_context().send_message(chat_id, "Unrecognized command or message!"
                                            + "\r\n" + "Send /help to see available commands.")

        else:
            print("un-implemented update type:", update)
