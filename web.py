#!/usr/bin/env python
import json
import logging
import uuid

import telebot
from bottle import Bottle, request, abort, run

from daysandbox_bot import init_bot_with_mode

app = Bottle()


def setup_web_app():
    logging.basicConfig(level=logging.DEBUG)
    bot = init_bot_with_mode('main')

    secret_key = str(uuid.uuid4())

    @app.route('/%s/' % secret_key, method='POST')
    def page():
        if request.headers.get('content-type') == 'application/json':
            json_string = request.body.read().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        else:
            abort(403)

    bot.remove_webhook()
    bot.set_webhook(url='https://telebot.grablab.org/daysandbox_bot/%s/' % secret_key)


setup_web_app()


if __name__ == '__main__':
    run(app, host='localhost', port=8888)
