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
            )
        """)
        self._db.commit()
        cu.close()

    def get_all(self):
        cu = self._db.cursor()
        ret = {
            word: proficiency for word, proficiency in cu.execute(
                "SELECT word, proficiency FROM `proficiency`"
            )
        }
        cu.close()
        return ret

    def count(self):
        cu = self._db.cursor()
        ret = {word: proficiency
               for word, proficiency
               in cu.execute("SELECT proficiency, COUNT(word) "
                             "FROM proficiency GROUP BY proficiency;")}
        cu.close()
        return ret

    def update(self, memory):
        cu = self._db.cursor()
        cu.executemany(
            "REPLACE INTO proficiency(word, proficiency) VALUES(?, ?)",
            list(memory.items())
        )
        self._db.commit()
        cu.close()
