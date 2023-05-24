import db
from model import Game, Participant
import time

import sqlite3
from sqlite3 import Error


PARTICIPANT_TABLE = \
        """
        CREATE TABLE IF NOT EXISTS participant (
                id integer PRIMARY KEY,
                game_id text NOT NULL,
                name text NOT NULL,
                accuracy real NOT NULL,
                time_entered real NOT NULL);
        """

PARTICIPANT_ENTRY = \
        """
        INSERT INTO participant (game_id,name,accuracy,time_entered)
        VALUES(?,?,?,?)
        """

GAME_TABLE = \
        """
        CREATE TABLE IF NOT EXISTS game (
                id text PRIMARY KEY,
                channel text NOT NULL,
                sentence text NOT NULL,
                time_started real NOT NULL);
        """

GAME_ENTRY = \
        """
        INSERT INTO game (id,channel,sentence,time_started) VALUES(?,?,?,?)
        """


# NOTE: This module is not thread-safe
class DB(db.DBInterface):
    _conn = None

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(DB, cls).__new__(cls)
        return cls.instance

    def __init__(self, db_file: str = "db.sqlite"):
        try:
            self._conn = sqlite3.connect(db_file)
            cur = self._conn.cursor()
            cur.execute(PARTICIPANT_TABLE)
            cur.execute(GAME_TABLE)
        except Error as e:
            print(e)

    def open(self):
        pass

    def close(self):
        # FIXME: close only if the reference counts are 0.
        if self._conn:
            self._conn.close()

    def insert(self, game: Game):
        cur = self._conn.cursor()
        cur.execute(GAME_ENTRY, (game.id, game.channel, game.sentence,
                                 game.time_started))
        for u in game.participants:
            cur.execute(PARTICIPANT_ENTRY, (game.id, u.id, u.accuracy,
                                            u.time_entered))
        self._conn.commit()

    def query_games(self, channel: str, time_window_sec: int) -> list[Game]:
        since = time.time() - time_window_sec
        cur = self._conn.cursor()
        cur.execute("SELECT * FROM game WHERE channel=? AND time_started > ?",
                    (channel, since))
        rows = cur.fetchall()

        games = []
        for row in rows:
            game = Game(id=row[0], channel=row[1], sentence=row[2],
                        time_started=row[3])
            games.append(game)

        return games

    def query_participants(self, game_id: str) -> list[Participant]:
        cur = self._conn.cursor()
        cur.execute("SELECT * FROM participant WHERE game_id=?", (game_id,))
        rows = cur.fetchall()

        participants = []
        for row in rows:
            participant = Participant(id=row[2], accuracy=row[3],
                                      time_entered=row[4])
            participants.append(participant)

        return participants


if __name__ == '__main__':
    t1 = DB()
    t2 = DB()
    if id(t1) != id(t2):
        print("Should be singleton")
