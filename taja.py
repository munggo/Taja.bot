import time
import random
import difflib
import uuid

from model import Game, Participant
import model

_sentences = open("data.txt", "r").read().splitlines()


def _calculate_speed(entered: str, elapsed_sec: time) -> float:
    """Returns words per minute(WPM)
    """
    return len(entered.encode('utf-8')) / elapsed_sec * 60


def _calculate_accuracy(expected: str, actual: str) -> float:
    diff = difflib.SequenceMatcher(None,
                                   expected.encode('utf-8'),
                                   actual.encode('utf-8'))
    return diff.ratio()


def _calculate_score(accuracy: float, wpm: float) -> int:
    return int(accuracy * wpm)


def _get_sentence(sentences: list[str] = None) -> str:
    if sentences is None:
        sentences = _sentences
    return random.choice(sentences).strip()


def start(channel: str = None) -> Game:
    return Game(id=uuid.uuid4(), channel=channel, sentence=_get_sentence(),
                time_started=time.time())


def report(game: Game, user_id: str, entered_sentece: str,
           timestamp: time) -> bool:
    # 1. check if the user already reported on the same game
    # 2. add user in the game
    user = Participant(id=user_id, accuracy=0, time_entered=timestamp)
    user.accuracy = _calculate_accuracy(game.sentence, entered_sentece)
    game.participants.append(user)
    # 3. add the game into database if not exists
    if len(game.participants) == 1:
        return model.save(game)
    #wpm = _calculate_speed(entered_sentece, timestamp - game.time_started)
    return True


def get_result(game: Game):
    # 1. calculate score per participants in the game
    # 2. print in the order of score
    return game


def find_game(channel: str = None, entered_sentece: str = None,
              time_window_sec: int = 15) -> Game:
    if entered_sentece is None:
        return None
    # 1. ignore if accuracy is less than 50%
    # FIXME: will not work on the same sentence occurence in the time window
    return model.query(channel, entered_sentece, time_window_sec)


if __name__ == "__main__":
    game = start()
    print(game)

    entered = input()
    report(game, "console user", entered, time.time())
    print(get_result(game))
