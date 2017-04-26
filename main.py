from packages.states.idlestate import IdleState
from packages.persistence.sqldbwrapper import SQLDBWrapper
from packages.bot.pelicanmarkdownbot import PelicanMarkdownBot
from packages.bot.mockbot import MockBot

import config

__author__ = "anaeanet"


def main():
    url = config.url.format(config.token)
    start_state_class = IdleState
    database = SQLDBWrapper(config.database_name)
    authorized_users = config.authorized_users

    bot = PelicanMarkdownBot(url, start_state_class, database, authorized_users=authorized_users)
    #bot = MockBot(url, start_state_class, database, authorized_users=authorized_users)
    bot.run()


if __name__ == "__main__":
    main()
