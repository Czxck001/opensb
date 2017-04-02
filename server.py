# encoding: utf-8
import asyncio
import os
import sys
import logging
import json
import argparse

import tornado
import tornado.web
import tornado.autoreload

from tornado.platform.asyncio import AsyncIOMainLoop

from database import MemoryDatabase
from logic import CoreLogic, CoreLogicConfig
from wordapi import WordGroupHandler, MemoryCountingHandler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

__frontend_path = os.path.join(BASE_DIR, 'frontend')
__static_path = os.path.join(__frontend_path, 'static')


def main():
    parser = argparse.ArgumentParser(description='OpenSB')
    parser.add_argument('-wb', '--wordbook',
                        help='Wordbook JSON')
    parser.add_argument('-db', '--database', default='memory.db',
                        help='Database (of the memory)')
    parser.add_argument('-o', '--override', nargs='*', default=[],
                        help='Override configuration, with k-v pairs')
    FLAGS = parser.parse_args()

    with open(FLAGS.wordbook) as f:
        wordbook = json.load(f)

    # override the configuration in command line (-o)
    config = CoreLogicConfig()
    for key, value in zip(*[iter(FLAGS.override)]*2):
        if not hasattr(config, key):
            print("WARNING: Invalid override with attribute %s" % (key))
        else:
            setattr(config, key, type(getattr(config, key))(value))

    mdb = MemoryDatabase(FLAGS.database)
    logic = CoreLogic(wordbook=wordbook, memory=mdb.get_all(), config=config)

    logging.basicConfig(
        stream=sys.stdout, level=logging.INFO,
        format='[%(asctime)s] %(name)s:%(levelname)s: %(message)s'
    )

    AsyncIOMainLoop().install()
    app_kwargs = {}
    # debug
    app_kwargs['debug'] = True
    app = tornado.web.Application([
        (r'/()', tornado.web.StaticFileHandler, {
            'path': __frontend_path,
            'default_filename': 'index.html'
        }),
        (r'/static/(.*)', tornado.web.StaticFileHandler, {
            'path': __static_path
        }),
        (r'/api/words', WordGroupHandler, {'logic': logic, 'mdb': mdb}),
        (r'/api/counting', MemoryCountingHandler, {'mdb': mdb}),
    ], **app_kwargs)
    app.listen(8081, address="0.0.0.0")
    loop = asyncio.get_event_loop()
    print('Reload.')
    loop.run_forever()


if __name__ == '__main__':
    main()
