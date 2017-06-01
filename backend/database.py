# encoding: utf-8

from threading import Thread
from functools import wraps
import sqlite3


def async_func(func):
    @wraps(func)
    def asyncf(*args, **kwargs):
        func_h = Thread(target = func, args = args, kwargs = kwargs)
        func_h.start()
        return func_h

    return asyncf

class MemoryDatabase:
    def __init__(self, db_path):
        self._db = sqlite3.connect(db_path)
        self.db_path = db_path
        # prepare database
        cu = self._db.cursor()
        cu.execute("""
            CREATE TABLE IF NOT EXISTS `proficiency` (
                `word` TEXT,
                `proficiency` INTEGER NOT NULL,
                PRIMARY KEY(`word`)
            );
        """)
        cu.execute("""
            CREATE TABLE IF NOT EXISTS `log` (
                id    INTEGER  PRIMARY KEY AUTOINCREMENT
                               NOT NULL,
                time  DATETIME NOT NULL,
                word  STRING   NOT NULL,
                known BOOLEAN  NOT NULL
            );
        """)
        self._db.commit()
        cu.close()

    def get_memory(self):
        cu = self._db.cursor()
        ret = {
            word: proficiency for word, proficiency in cu.execute(
                "SELECT word, proficiency FROM `proficiency`"
            )
        }
        cu.close()
        return ret

    @async_func
    def update_memory(self, memory):
        db = sqlite3.connect(self.db_path)
        cu = db.cursor()
        cu.executemany(
            "REPLACE INTO proficiency(word, proficiency) VALUES(?, ?)",
            list(memory.items())
        )
        db.commit()
        cu.close()

    @async_func
    def log_word(self, word, known):
        import datetime
        db = sqlite3.connect(self.db_path)
        cu = db.cursor()
        cu.execute(
            "INSERT INTO log(time, word, known) VALUES(?, ?, ?)",
            (datetime.datetime.now(), word, known)
        )
        db.commit()
        cu.close()
