import json

from packages.bot.pelicanmarkdownbot import PelicanMarkdownBot

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


class MockBot(PelicanMarkdownBot):

    def __init__(self, token):
        super().__init__(token)
        self.__sequence = Sequence()

    def get_updates(self, offset=None):
        userinput = input("enter message to bot: ")
        content = EMPTYRESPONSE1 + str(self.__sequence.get()) + EMPTYRESPONSE2 + '"' + str(userinput) + '"' + EMPTYRESPONSE3
        js = json.loads(content)
        return js

    def send_message(self, chat_id, content):
        if "text" in content:
            print(content["text"])
