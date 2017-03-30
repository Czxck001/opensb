# encoding: utf-8
import asyncio
import os
import sys
import logging
import json
import sqlite3
import argparse

import tornado
import tornado.web
import tornado.autoreload

from tornado.platform.asyncio import AsyncIOMainLoop

from wordapi import WordHandler
from wordapi import CountingHandler
from logic import CoreLogic

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

__frontend_path = os.path.join(BASE_DIR, 'frontend')
__static_path = os.path.join(__frontend_path, 'static')


def prepare_db(db):
    cu = db.cursor()
    cu.execute("""
        CREATE TABLE IF NOT EXISTS `word` (
            `id` INTEGER PRIMARY KEY AUTOINCREMENT,
            `word` TEXT NOT NULL UNIQUE,
            `detail` TEXT
        )
    """)
    cu.execute("""
        CREATE TABLE IF NOT EXISTS `proficiency` (
            `word` TEXT,
            `proficiency` INTEGER NOT NULL,
            PRIMARY KEY(`word`)
        )
    """)
    db.commit()
    cu.close()


def get_words(db):
    cu = db.cursor()
    ret = {word: text for word, text in cu.execute("SELECT word, detail FROM `word` ORDER BY `id`")}
    cu.close()
    return ret


def get_proficiency(db):
    cu = db.cursor()
    ret = {word: proficiency for word, proficiency in cu.execute("SELECT word, proficiency FROM `proficiency`")}
    cu.close()
    return ret


def get_argparser():
    parser = argparse.ArgumentParser(description='OpenSB')
    parser.add_argument('-i', '--import-dict', help='import dictionary')
    parser.add_argument('-d', '--database', help='path to database',
                        default='opensb.db')

    return parser


def get_app(db):
    wordlist = get_words(db)
    memory = get_proficiency(db)
    logic = CoreLogic(wordlist=wordlist, memory=memory)

    app_kwargs = {}
    # debug
    app_kwargs['debug'] = True
    application = tornado.web.Application([
        (r'/()', tornado.web.StaticFileHandler, {
            'path': __frontend_path,
            'default_filename': 'index.html'
        }),
        (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': __static_path}),
        (r'/api/words', WordHandler, {'logic': logic, 'db': db}),
        (r'/api/counting', CountingHandler, {'db': db}),
    ], **app_kwargs)
    return application


def start_server(db):
    AsyncIOMainLoop().install()
    app = get_app(db)
    app.listen(8081, address="0.0.0.0")
    loop = asyncio.get_event_loop()
    print('Reload.')
    loop.run_forever()


def main():
    parser = get_argparser()
    args = parser.parse_args()

    logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                        format='[%(asctime)s] %(name)s:%(levelname)s: %(message)s')
    db = sqlite3.connect(args.database)
    prepare_db(db)

    if args.import_dict:
        dictionary = json.load(open(args.import_dict, 'r'))
        cu = db.cursor()
        cu.executemany("REPLACE INTO word(word, detail) VALUES (?, ?)", dictionary)
        db.commit()
        cu.close()

    start_server(db)


if __name__ == '__main__':
    main()
