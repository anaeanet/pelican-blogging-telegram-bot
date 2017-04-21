from packages.persistence.dbwrapper import DBWrapper
from packages.bot.telegrambot import TelegramBot
from packages.bot.mockbot import MockBot

__author__ = "anaeanet"


def main():
    db = DBWrapper()
    db.setup()
    bot = TelegramBot(db)
    #bot = MockBot(db)
    bot.run()


if __name__ == "__main__":
    main()
