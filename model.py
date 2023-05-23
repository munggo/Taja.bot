import uuid
import time
from dataclasses import dataclass, field


@dataclass
class Participant:
    id: str
    accuracy: float
    time_entered: time


@dataclass
class Game:
    id: uuid
    channel: str
    sentence: str
    time_started: time
    participants: list[Participant] = field(default_factory=list)


def query(channel: str, entered_sentence: str, time_window_sec: int) -> Game:
    pass


def save(game: Game) -> bool:
    pass
