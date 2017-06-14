from packages.persistence.dbwrapper2 import DBWrapper2
from packages.bot.pelicanmarkdownbot2 import PelicanMarkdownBot2
from packages.bot.parsemode import ParseMode

import config

__author__ = "anaeanet"


def main():
    token = config.token
    url = config.url
    file_url = config.file_url
    database = DBWrapper2(config.database_name)
    authorized_users = config.authorized_users

    post_target_url = config.markdown_target
    gallery_target_url = config.gallery_target

    bot = PelicanMarkdownBot2(token, url, file_url, database, post_target_url, gallery_target_url, authorized_users=authorized_users)
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
