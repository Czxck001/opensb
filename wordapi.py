# encoding: utf-8
import tornado.web


class WordHandler(tornado.web.RequestHandler):

    def initialize(self, logic):
        self.logic = logic

    def get(self):
        words = self.logic.next_group()
        self.write({'words': words})

    def post(self):
        pass
