from telegram import Bot

from daysandbox_bot import get_token


def setup_arg_parser(parser):
    parser.add_argument('mode')
    parser.add_argument('chat_id', type=int)


def main(mode, chat_id, **kwargs):
    bot = Bot(token=get_token('test'))
    res = bot.leave_chat(chat_id)
