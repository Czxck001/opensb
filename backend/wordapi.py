# encoding: utf-8
import json
import tornado.web


class WordGroupHandler(tornado.web.RequestHandler):

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
        self.logic.update_group(know_status)

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
        self.logic.make_task(
            max_prof=post_data['max_prof'],
            num_new_word=post_data['num_new_word'],
            task_size=post_data['task_size']
        )


class StatusHandler(tornado.web.RequestHandler):

    def initialize(self, logic):
        self.logic = logic

    def get(self):
        self.write({
            'progress': self.logic.count_progress(),
            'config': {
                attr: getattr(self.logic.config, attr)
                for attr in dir(self.logic.config)
                if not attr.startswith('__')
            }
        })
