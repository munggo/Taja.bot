import threading
import time
import random
import difflib
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

SENTENCES = open("data.txt", "r").read().splitlines()
SENTENCES_ENG = open("eng.txt", "r").read().splitlines()
games = {}
game_lock = threading.Lock()

SLACK_APP_TOKEN = "SLACK_APP_TOKEN"
SLACK_BOT_TOKEN = "SLACK_BOT_TOKEN"

app = App(token=SLACK_BOT_TOKEN)
selected_sentence = ""
start_time = 0

client = WebClient(token=SLACK_BOT_TOKEN)


def get_display_name(user_id):
    try:
        user_info = client.users_info(user=user_id)
        display_name = user_info["user"]["profile"]["display_name"]
    except SlackApiError as e:
        display_name = None
        print(f"Error getting user info: {e}")
    return display_name


def replace_spaces(sentence):
    chars = list(sentence)
    for i in range(len(chars)):
        if chars[i] == " ":
            chars[i] = random.choice(['~', '+', '-', '_', '=', '^'])
    return "".join(chars)


def typing_speed(num_chars, end_time):
    global selected_sentence
    return int((num_chars / end_time) * 60)


def typing_accuracy(entered_sentence, correct_sentence):
    ori = correct_sentence.split()
    ent = entered_sentence.split()
    sm = difflib.SequenceMatcher(None, correct_sentence.encode('utf-8'), entered_sentence.encode('utf-8'))
    ratio = sm.ratio()
    return int(ratio * 100)


def game_thread(channel_id, users, members, selected_sentence):
    global start_time
    global games
    displayed_sentence = replace_spaces(selected_sentence)
    try:
        time.sleep(2)
        disp_message = "*" + displayed_sentence + "*"
        response = client.chat_postMessage(channel=channel_id, text=disp_message)
    except SlackApiError as e:
        print(f"Error sending message: {e}")

    start_time = time.time()
    end_time = 20
    positions = {}
    while end_time > 0:
        time.sleep(1)
        end_time = end_time - 1

    result = sorted(users, key=lambda x: (x["accuracy"], x["wpm"]), reverse=True)
    text = "\n".join(
        [
            f"{i + 1}. {get_display_name(r['user'])}: {r['accuracy']}% / {r['wpm']} 타수/분"
            for i, r in enumerate(result)
        ]
    )
    try:
        response = client.chat_postMessage(
            channel=channel_id,
            text=f"게임이 종료되었습니다.\n{text}"
        )
    except SlackApiError as e:
        print(f"Error sending message: {e}")
    with game_lock:
        del games[channel_id]


@app.event("app_mention")
def handle_mention(event, say):
    global games
    global selected_sentence
    global start_time
    global client
    channel_id = event["channel"]
    with game_lock:
        if channel_id in games:
            say("이미 게임이 진행 중입니다.")
            return
        try:
            members = client.conversations_members(channel=channel_id, limit=100)["members"]
        except SlackApiError as e:
            print("Error getting members:", e)
            members = []
        games[channel_id] = {"users": [], "game_thread": None}

        if '영문' in event['text'] or 'eng' in event['text']:
            selected_sentence = random.choice(SENTENCES_ENG).strip()
        elif '랜덤' in event['text'] or 'random' in event['text']:
            random_sentence = list()
            random_sentence.append(random.choice(SENTENCES_ENG).strip())
            random_sentence.append(random.choice(SENTENCES).strip())
            selected_sentence = random.choice(random_sentence)
        else:
            selected_sentence = random.choice(SENTENCES).strip()
        games[channel_id]["game_thread"] = threading.Thread(
            target=game_thread, args=(channel_id, games[channel_id]["users"], members, selected_sentence)
        )
        games[channel_id]["game_thread"].daemon = True
        games[channel_id]["game_thread"].start()
        say(f"2초 뒤 제시된 문장을 20초 안에 입력하세요. (게임이 종료되기 전 마지막 채팅 기록으로 결과를 측정합니다)")
    users = games[channel_id]["users"]
    start_time = time.time()


@app.event("message")
def handle_message(event, say):
    global games
    global selected_sentence
    global start_time
    channel_id = event["channel"]

    with game_lock:
        if channel_id not in games:
            return
        users = games[channel_id]["users"]

    if "subtype" not in event or event["subtype"] not in ["bot_message", "message_deleted"]:
        user_id = event["user"]
        text = event["text"]
        with game_lock:
            for i, user_obj in enumerate(users):
                if user_obj["user"] == user_id:
                    break
            else:
                users.append({"user": user_id, "entered_sentence": "", "accuracy": 0, "wpm": 0})
                i = len(users) - 1

        accuracy = typing_accuracy(text, selected_sentence)
        end_time = time.time() - start_time
        wpm = typing_speed(len(selected_sentence.encode('utf-8')), end_time)

        with game_lock:
            users[i]["accuracy"] = accuracy
            users[i]["wpm"] = wpm

            if len(users) == len(games[channel_id]["users"]) and games[channel_id]["game_thread"].is_alive():
                games[channel_id]["game_thread"].join(timeout=0)

    with game_lock:
        if not games[channel_id]["game_thread"].is_alive():
            del games[channel_id]


if __name__ == "__main__":
    handler = SocketModeHandler(app_token=SLACK_APP_TOKEN, app=app)
    handler.start()
