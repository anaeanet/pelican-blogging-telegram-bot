# pelican-blogging-telegram-bot

Are you running a [Pelican](http://docs.getpelican.com) blog? 
Do you use the [Telegram](https://telegram.org) messenger app?
Then combine the two to enhance your mobile blogging experience!

## Introduction

under construction...

## config.py

    url = "https://api.telegram.org/bot"
    file_url = "https://api.telegram.org/file/bot"
    token = "<BOT_TOKEN>"
    post_target = "<SERVER>:<POST_PATH>/"
    gallery_target = "<SERVER>:<GALLERY_PATH>/"
    authorized_users = [
        {"id":<USER1_ID>, "name":"<USER1_NAME>"} 
        , {"id":<USER2_ID>, "name": "<USER2_NAME>"} 
        , ...
    ]