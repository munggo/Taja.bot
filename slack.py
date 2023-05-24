import os
import time
import taja

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

APP_TOKEN = os.environ["SLACK_TAJA_APP_TOKEN"]
BOT_TOKEN = os.environ["SLACK_TAJA_BOT_TOKEN"]

app = App(token=BOT_TOKEN)


@app.event("app_mention")
def on_mention(event, say):
    game = taja.start(event["channel"])
    say(game.sentence)


@app.event("message")
def on_message(event, say):
    timestamp = time.time()
    channel = event["channel"]
    user = event["user"]
    entered = event["text"]

    game = taja.find_game_by_sentence(channel, entered)
    if game is None:
        return

    if taja.report(game, user, entered, timestamp) is True:
        result = taja.get_result(game)
        say(result)


if __name__ == "__main__":
    handler = SocketModeHandler(app_token=APP_TOKEN, app=app)
    handler.start()
