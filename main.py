from packages.bot.pelicanmarkdownbot import PelicanMarkdownBot
from packages.bot.mockbot import MockBot

__author__ = "anaeanet"


def main():
    bot = PelicanMarkdownBot()
    #bot = MockBot()
    bot.run()


if __name__ == "__main__":
    main()
