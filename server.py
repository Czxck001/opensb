# encoding: utf-8
import asyncio
import os
import sys
import logging

import tornado
import tornado.web
import tornado.autoreload

from tornado.platform.asyncio import AsyncIOMainLoop


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

__frontend_path = os.path.join(BASE_DIR, 'frontend')
__static_path = os.path.join(__frontend_path, 'static')


def get_app():
    app_kwargs = {}
    # debug
    app_kwargs['debug'] = True
    application = tornado.web.Application([
        (r'/()', tornado.web.StaticFileHandler, {
            'path': __frontend_path,
            'default_filename': 'index.html'
        }),
    ], **app_kwargs)
    return application


def start_server():
    AsyncIOMainLoop().install()
    app = get_app()
    app.listen(8081)
    loop = asyncio.get_event_loop()
    print('Reload.')
    loop.run_forever()


def main():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                        format='[%(asctime)s] %(name)s:%(levelname)s: %(message)s')
    start_server()


if __name__ == '__main__':
    main()
