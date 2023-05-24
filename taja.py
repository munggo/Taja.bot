import time
import random
import difflib
import uuid

import db
from model import Game, Participant


class Taja:
    def __init__(self, data_file: str = "data.txt", db: db.DBInterface = None):
        self._sentences = open(data_file, "r").read().splitlines()
        self._db = db

    def _get_sentence(self) -> str:
        return random.choice(self._sentences).strip()

    def start(self, channel: str = None) -> Game:
        return Game(id=str(uuid.uuid4()), channel=channel,
                    sentence=self._get_sentence(), time_started=time.time())

    def report(self, game: Game, user_id: str, entered_sentece: str,
               timestamp: time) -> bool:
        # 1. check if the user already reported on the same game
        if _has_participated(game.participants, user_id) is True:
            return False

        # 2. add user in the game
        user = Participant(id=user_id,
                           accuracy=_calculate_accuracy(game.sentence,
                                                        entered_sentece),
                           wpm=_calculate_speed(entered_sentece,
                                                timestamp - game.time_started),
                           time_entered=timestamp, score=0)
        game.participants.append(user)

        # 3. add the game into database if not exists
        if len(game.participants) == 1 and self._db is not None:
            return self._db.insert(game)

        return True

    # FIXME: not work correctly on the same sentence occurence in a time window
    def find_game_by_sentence(self, channel: str = None,
                               entered_sentece: str = None,
                               time_window_sec: int = 15) -> Game:
        if self._db is None or entered_sentece is None:
            return None

        games = self._db.query_games(channel, time_window_sec)
        for game in games:
            # assume it matches if accuracy is more than 50%
            if _calculate_accuracy(game.sentence, entered_sentece) > 0.5:
                participant = self._db.query_participants(game.id)
                game.participants.append(participant)
                return game
        return None

    def get_result(self, game: Game) -> Participant:
        participants = []
        for participant in game.participants:
            participant.score = _calculate_score(participant.accuracy,
                                                 participant.wpm)
            participants.append(participant)
        # TODO: sort in the order of score
        return participants


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


def _has_participated(participants: list[Participant], user_id: str):
    for participant in participants:
        if participant.id == user_id:
            return True
    return False
