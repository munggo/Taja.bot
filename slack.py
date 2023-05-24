import os
import time
import taja
import sqlite

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

import random

APP_TOKEN = os.environ["SLACK_TAJA_APP_TOKEN"]
BOT_TOKEN = os.environ["SLACK_TAJA_BOT_TOKEN"]

bot_app = App(token=BOT_TOKEN)
bot = WebClient(token=BOT_TOKEN)
db = sqlite.SQLite()
app = taja.Taja(db=db)


def replace_spaces(sentence):
    chars = list(sentence)
    for i in range(len(chars)):
        if chars[i] == " ":
            chars[i] = random.choice(['~', '+', '-', '_', '=', '^'])
    return "".join(chars)


@bot_app.event("app_mention")
def on_mention(event, say):
    game = app.start(event["channel"])
    say("*" + replace_spaces(game.sentence) + "*")


@bot_app.event("message")
def on_message(event, say):
    timestamp = time.time()
    channel = event["channel"]
    user = event["user"]
    entered = event["text"]

    game = app.find_game_by_sentence(channel, entered)
    if game is None:
        return

    if app.report(game, user, entered, timestamp) is True:
        participants = app.get_result(game)
        for participant in participants:
            user_info = bot.users_info(user=participant.id)
            name = user_info["user"]["profile"]["display_name"]
            text = name + ": " + \
                   str(int(participant.accuracy * 100)) + "% / " + \
                   str(int(participant.wpm)) + " 타수/분"
            say(text)


if __name__ == "__main__":
    handler = SocketModeHandler(app_token=APP_TOKEN, app=bot_app)
    handler.start()
