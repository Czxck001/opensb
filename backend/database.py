# encoding: utf-8
class MemoryDatabase:
    def __init__(self, db_path):
        import sqlite3
        self._db = sqlite3.connect(db_path)

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

    def update_memory(self, memory):
        cu = self._db.cursor()
        cu.executemany(
            "REPLACE INTO proficiency(word, proficiency) VALUES(?, ?)",
            list(memory.items())
        )
        self._db.commit()
        cu.close()

    def log_word(self, word, known):
        import datetime
        cu = self._db.cursor()
        cu.execute(
            "INSERT INTO log(time, word, known) VALUES(?, ?, ?)",
            (datetime.datetime.now(), word, known)
        )
        self._db.commit()
        cu.close()
