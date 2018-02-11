import logging
from queue import Queue
import uuid
import json
from threading import Thread

from bottle import request, abort
from telegram import Update
from telegram.ext import Dispatcher

from daysandbox_bot import init_bot_with_mode, register_handlers


def setup_web_app(app, mode='production'):
    logging.basicConfig(level=logging.DEBUG)
    bot = init_bot_with_mode(mode)
    update_queue = Queue()
    dispatcher = Dispatcher(bot, update_queue, workers=16)
    #dispatcher = Dispatcher(bot, None, workers=0)
    register_handlers(dispatcher, mode)

    thread = Thread(target=dispatcher.start, name='dispatcher')
    thread.start()

    secret_key = str(uuid.uuid4())

    @app.route('/%s/' % secret_key, method='POST')
    def page():
        if request.headers.get('content-type') == 'application/json':
            json_string = request.body.read().decode('utf-8')
            update = Update.de_json(json.loads(json_string), bot)
            dispatcher.process_update(update)
            return ''
        else:
            abort(403)

    config = json.load(open('var/config.json'))
    key = 'test_webhook_url' if mode == 'test' else 'webhook_url'
    url = config[key] % {'secret_key': secret_key}
    logging.debug('Webhook has been set to %s' % url)
    bot.set_webhook(url=url)
