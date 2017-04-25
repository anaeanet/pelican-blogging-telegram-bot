from packages.bot.pelicanmarkdownbot import PelicanMarkdownBot
from packages.bot.state.idlestate import IdleState
from packages.bot.mockbot import MockBot

import config

__author__ = "anaeanet"


def main():
    bot = PelicanMarkdownBot(config.url.format(config.token), IdleState, config.authorized_users)
    #bot = MockBot(config.url.format(config.token), IdleState, config.authorized_users)
    bot.run()


if __name__ == "__main__":
    main()
