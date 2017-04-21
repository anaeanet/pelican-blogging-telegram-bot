from packages.bot.telegrambot import TelegramBot

__author__ = "anaeanet"


EMPTYRESPONSE1 = '{"ok":true,"result":[{"update_id":'
EMPTYRESPONSE2 = ',"message":{"message_id":1,"from":{"id":1,"first_name":"Anja","last_name":"Fischer","username":"anaea_net"},"chat":{"id":1,"first_name":"Anja","last_name":"Fischer","username":"anaea_net","type":"private"},"date":1478087624,"text":'
EMPTYRESPONSE3 = '}}]}'


class Sequence:

    def __init__(self, index=0):
        self.__index = index

    def get(self):
        self.__index += 1
        return self.__index - 1


class MockBot(TelegramBot):

    def __init__(self, database):
        super().__init__(database)
        self.__sequence = Sequence()

    def get_url_response(self, url):
        if "getUpdates?timeout" in url:
            content = input("enter message to bot: ")
            content = EMPTYRESPONSE1 + str(self.__sequence.get()) + EMPTYRESPONSE2 + '"' + str(content) + '"' + EMPTYRESPONSE3
        else:
            content = '{"ok":true,"result":[]}'
        return content

    def send_message(self, chat_id, text, reply_markup=None, parse_mode=None):
        print(text)
        super().send_message(chat_id, text, reply_markup=None, parse_mode=None)
