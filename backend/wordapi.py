# encoding: utf-8
import json
import tornado.web


class WordGroupHandler(tornado.web.RequestHandler):

    def initialize(self, logic, mdb):
        self.logic = logic
        self.mdb = mdb

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
        self.mdb.update(self.logic.memory)

        words, progress = self.logic.next_group()
        self.write({
            'words': words,
            'progress': progress
        })


class MemoryCountingHandler(tornado.web.RequestHandler):

    def initialize(self, logic):
        self.logic = logic

    def get(self):
        self.write(self.logic.count_memory())


class NewTaskHandler(tornado.web.RequestHandler):

    def initialize(self, logic):
        self.logic = logic

    def post(self):
        post_data = json.loads(self.request.body.decode('utf-8'))
        self.logic.make_task(**post_data)


class ConfigHandler(tornado.web.RequestHandler):

    def initialize(self, logic):
        self.logic = logic

    def get(self):
        self.write({
            attr: getattr(self.logic.config, attr)
            for attr in dir(self.logic.config)
            if not attr.startswith('__')
        })
