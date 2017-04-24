from packages.bot.pelicanmarkdownbot import PelicanMarkdownBot
from packages.bot.mockbot import MockBot

import config

__author__ = "anaeanet"


def main():
    bot = PelicanMarkdownBot(config.token)
    #bot = MockBot(config.token)
    bot.run()


if __name__ == "__main__":
    main()
