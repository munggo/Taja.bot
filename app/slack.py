import os
import time
from taja import taja
from taja import sqlite

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

import random
import threading

APP_TOKEN = os.environ["SLACK_TAJA_APP_TOKEN"]
BOT_TOKEN = os.environ["SLACK_TAJA_BOT_TOKEN"]

bot_app = App(token=BOT_TOKEN)
bot = WebClient(token=BOT_TOKEN)
db = sqlite.SQLite()
app = taja.Taja(db=db)
locks = {}


def on_timeout(channel):
    locks[channel].release()
    print(time.ctime())


@bot_app.event("app_mention")
def on_mention(event, say):
    if not event["channel"] in locks:
        locks[event["channel"]] = threading.Semaphore(1)
    if locks[event["channel"]].acquire(blocking=False) is False:
        say("이미 게임이 진행 중입니다.")
        return

    game = app.start(event["channel"])
    sentence = game.sentence.replace(" ", random.choice(['-', '_']))
    say("*" + sentence + "*")
    # TODO: Parse the message and hand over how many participants there will be.
    threading.Timer(15, on_timeout, [event["channel"]]).start()


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
