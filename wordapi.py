# encoding: utf-8
import json
import tornado.web


class WordHandler(tornado.web.RequestHandler):

    def initialize(self, logic):
        self.logic = logic

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
        words, progress = self.logic.next_group()
        self.write({
            'words': words,
            'progress': progress
        })
