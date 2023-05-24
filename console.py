import taja
import sqlite
import time


if __name__ == "__main__":
    db = sqlite.SQLite()
    app = taja.Taja(db=db)

    game = app.start("console")
    print(game)
    entered = input()
    app.report(game, "console user", entered, time.time())
    print(app.get_result(game))
