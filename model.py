import uuid
import time
from dataclasses import dataclass, field


@dataclass
class Participant:
    id: str
    accuracy: float
    wpm: float
    time_entered: time
    score: int


@dataclass
class Game:
    id: uuid
    channel: str
    sentence: str
    time_started: time
    participants: list[Participant] = field(default_factory=list)
