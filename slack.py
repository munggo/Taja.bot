import os
import time
import taja
import sqlite

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

APP_TOKEN = os.environ["SLACK_TAJA_APP_TOKEN"]
BOT_TOKEN = os.environ["SLACK_TAJA_BOT_TOKEN"]

bot = App(token=BOT_TOKEN)
db = sqlite.SQLite()
app = taja.Taja(db=db)


@bot.event("app_mention")
def on_mention(event, say):
    game = app.start(event["channel"])
    say(game.sentence)


@bot.event("message")
def on_message(event, say):
    timestamp = time.time()
    channel = event["channel"]
    user = event["user"]
    entered = event["text"]

    game = app.find_game_by_sentence(channel, entered)
    if game is None:
        return

    if app.report(game, user, entered, timestamp) is True:
        result = app.get_result(game)
        say(result)


if __name__ == "__main__":
    handler = SocketModeHandler(app_token=APP_TOKEN, app=bot)
    handler.start()
