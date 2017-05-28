from packages.states.idlestate import IdleState
from packages.persistence.sqldbwrapper import SQLDBWrapper
from packages.bot.pelicanmarkdownbot import PelicanMarkdownBot
from packages.bot.mockbot import MockBot
from packages.bot.parsemode import ParseMode

import config

__author__ = "anaeanet"


def main():
    url = config.url.format(config.token)
    start_state_class = IdleState
    database = SQLDBWrapper(config.database_name)
    authorized_users = config.authorized_users

    bot = PelicanMarkdownBot(url, start_state_class, database, authorized_users=authorized_users)
    #bot = MockBot(url, start_state_class, database, authorized_users=authorized_users)

    try:
        bot.run()
    except Exception as e:
        # inform all authorized users about crashing blogging bot
        for user_id in authorized_users:
            bot.send_message(user_id
                             , "BloggingBot was terminated unexpectedly!"
                             + "\r\n\r\n"
                             + "*" + str(type(e)) + "*" + "\r\n"
                             + "{}".format(e)
                             , parse_mode=ParseMode.MARKDOWN.value)


if __name__ == "__main__":
    main()
