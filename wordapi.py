# encoding: utf-8
import json
import tornado.web


class WordHandler(tornado.web.RequestHandler):

    def initialize(self, logic, db):
        self.logic = logic
        self.db = db

    def get(self):
        words, progress = self.logic.next_group()
        self.write({
            'words': words,
            'progress': progress
        })

    def post(self):
        post_data = json.loads(self.request.body.decode('utf-8'))
        know_status = post_data.get('knowStatus', {})
        for word, know in know_status.items():
            if know:
                self.logic.i_know(word)
            else:
                self.logic.i_dont_know(word)

        # save proficiency
        self.logic.update_memory()
        cu = self.db.cursor()
        cu.executemany(
            "REPLACE INTO proficiency(word, proficiency) VALUES(?, ?)",
            [(word, proficiency) for word, proficiency in self.logic.memory.items()]
        )
        self.db.commit()
        cu.close()

        words, progress = self.logic.next_group()
        self.write({
            'words': words,
            'progress': progress
        })


class CountingHandler(tornado.web.RequestHandler):

    def initialize(self, db):
        self.db = db

    def get(self):
        cu = self.db.cursor()
        ret = {word: proficiency
               for word, proficiency in cu.execute("SELECT proficiency, COUNT(word) FROM proficiency GROUP BY proficiency;")
               }
        cu.close()
        self.write(ret)
