import abc
from model import Game, Participant


class DBInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, "open") and callable(subclass.open) and
                hasattr(subclass, "close") and callable(subclass.close) and
                hasattr(subclass, "insert") and callable(subclass.insert) and
                hasattr(subclass, "query_games") and
                callable(subclass.query_games) and
                hasattr(subclass, "query_participants") and
                callable(subclass.query_participants))

    @abc.abstractmethod
    def open(self):
        raise NotImplementedError

    @abc.abstractmethod
    def close(self):
        raise NotImplementedError

    @abc.abstractmethod
    def query_games(self, channel: str, time_window_sec: int) -> list[Game]:
        raise NotImplementedError

    @abc.abstractmethod
    def query_participants(self, game_id: str) -> list[Participant]:
        raise NotImplementedError
