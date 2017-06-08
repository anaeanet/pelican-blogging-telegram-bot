from packages.states.navigation.idlestate import IdleState
from packages.persistence.sqldbwrapper import SQLDBWrapper
from packages.bot.pelicanmarkdownbot import PelicanMarkdownBot
from packages.bot.parsemode import ParseMode

import config

__author__ = "anaeanet"


def main():
    token = config.token
    url = config.url
    file_url = config.file_url
    database = SQLDBWrapper(config.database_name)
    authorized_users = config.authorized_users

    bot = PelicanMarkdownBot(token, url, file_url, database, authorized_users=authorized_users)
    bot.run()   # TODO once development is finished, remove row

    try:
        bot.run()
    except Exception as e:

        # TODO log error

        # inform all authorized users about crashing blogging bot
        for user_id in authorized_users:
            bot.send_message(user_id
                             , "BloggingBot was terminated unexpectedly!"
                             + "\r\n\r\n"
                             + "*" + str(type(e)) + "*" + "\r\n"
                             + "{}".format(e)
                             , parse_mode=ParseMode.HTML.value)


if __name__ == "__main__":
    main()
