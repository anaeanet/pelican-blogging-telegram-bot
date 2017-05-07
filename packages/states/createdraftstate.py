from packages.states.abstractstate import AbstractState
from packages.bot.parsemode import ParseMode
import packages.bot.telegram as telegram

__author__ = "aneanet"


class CreateDraftState(AbstractState):
    """
    Concrete state implementation.
    """

    def __init__(self, context, chat_id=None, user_id=None):
        super().__init__(context)

        if chat_id is not None:
            self.get_context().send_message(chat_id
                                            , "Enter the *title* of your new draft:"
                                            , parse_mode=ParseMode.MARKDOWN.value)

    def process_update(self, update):
        update_type = telegram.get_update_type(update)

        # --------------------------------------------------------------------------------------------------------------
        # message
        # --------------------------------------------------------------------------------------------------------------
        if update_type == "message":
            user_id = telegram.get_update_sender_id(update)
            chat_id = update[update_type]["chat"]["id"]
            text = update[update_type]["text"].strip(' \t\n\r') if "text" in update[update_type] else None

            # ----------------------------------------------------------------------------------------------------------
            # user entered text
            # ----------------------------------------------------------------------------------------------------------
            if text:
                # for global commands simply run code of IdleState
                if text in ["/start", "/help", "/createdraft", "/updatedraft", "/deletedraft"] or text.startswith("/"):
                    from packages.states.idlestate import IdleState
                    IdleState(self.get_context()).process_update(update)

                # plain text message, does not contain bot_commands, urls, ...
                elif "entities" not in update[update_type]:
                    self.get_context().add_post(user_id, text)
                    self.get_context().send_message(chat_id
                                                    , "Successfully created draft '*" + text + "*'"
                                                    , parse_mode=ParseMode.MARKDOWN.value)
                    from packages.states.idlestate import IdleState
                    self.get_context().set_user_state(user_id, IdleState(self.get_context()))

                # invalid - text message containing bot_command, url, ...
                else:
                    self.get_context().send_message(chat_id
                                                    , "'*" + text + "*' is not a valid draft title!"
                                                    + "\r\n" + " Please enter plain text only:"
                                                    , parse_mode=ParseMode.MARKDOWN.value)

            else:
                self.get_context().send_message(chat_id
                                                , "Unrecognized command or message!"
                                                + "\r\n" + "Send /help to see available commands."
                                                , parse_mode=ParseMode.MARKDOWN.value)

        # --------------------------------------------------------------------------------------------------------------
        # unsupported update type
        # --------------------------------------------------------------------------------------------------------------
        else:
            print("unsupported update type:", update_type)  # TODO change to log rather than print
