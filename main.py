from packages.persistence.dbwrapper import DBWrapper
from packages.bot.pelicanbot import PelicanBot
from packages.bot.telegrambot import TelegramBot

__author__ = "anaeanet"


def main():
    db = DBWrapper()
    db.setup()
    bot = TelegramBot(db)
    bot.run()


if __name__ == "__main__":
    main()
