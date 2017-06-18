from packages.persistence.dbwrapper import DBWrapper
from packages.bot.pelicanmarkdownbot import PelicanMarkdownBot

import logging
import logging.config
import config

__author__ = "anaeanet"


def main():
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger("pelicanblogbot")

    logger.info("starting pelicanBlogBot")

    try:
        token = config.token
        url = config.url
        file_url = config.file_url
        authorized_users = config.authorized_users

        post_target_url = config.post_target
        gallery_target_url = config.gallery_target

        bot = PelicanMarkdownBot(token, url, file_url, DBWrapper(), post_target_url, gallery_target_url,
                                 authorized_users=authorized_users)
        # start bot
        bot.run()

    except (NameError, AttributeError) as e:
        logger.exception("Config incomplete, PelicanMarkdownBot could not be instantiated!")
        raise

    except Exception as e:
        logger.exception("Bot crashed!")

        # inform all authorized users about crashing blogging bot
        for user_id in authorized_users:
            bot.send_message(user_id, "BloggingBot was terminated unexpectedly!")

        raise

if __name__ == "__main__":
    main()
