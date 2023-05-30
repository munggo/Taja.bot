from taja import taja
from taja import sqlite
import time


if __name__ == "__main__":
    db = sqlite.SQLite()
    app = taja.Taja(db=db)

    game = app.start("console")
    print(game.sentence)

    entered = input()

    game = app.find_game_by_sentence("console", entered)
    if game is not None:
        app.report(game, "console user", entered, time.time())
        participants = app.get_result(game)
        for participant in participants:
            text = participant.id + ": " + \
                   str(int(participant.accuracy * 100)) + "% / " + \
                   str(int(participant.wpm)) + " 타수/분 / " + \
                   str(int(participant.score))
            print(text)
