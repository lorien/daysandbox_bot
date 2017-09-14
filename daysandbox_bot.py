#!/usr/bin/env python
from collections import Counter
import json
import logging
import telebot
from argparse import ArgumentParser
from pymongo import MongoClient
from datetime import datetime, timedelta

HELP = """*DaySandBox Bot Help*

This bot implements simple anti-spam technique - it deletes all posts which:
1. contains link or mentions not-the-group's member username or forwarded from somewhere
2. AND posted by the user who has joined the group less than 24 hours ago

This bot does not ban anybody, it only deletes messages by the rules listed above.
The idea is that in these 24 hours the spamer would be banned anyway for posting spam to
other groups that are not protected by [@daysandbox_bot](https://t.me/daysandbox_bot).

*Usage*

1. Add [@daysandbox_bot](https://t.me/daysandbox_bot) to your group.
2. Go to group settings / users list / promote user to admin
3. Enable only one item: Delete messages
4. Click SAVE button
5. Enjoy!

*Commands*

/help - display this help message
/stat - display simple statistics about number of deleted messages

*Open Source*

The source code is available at [github.com/lorien/daysandbox_bot](https://github.com/lorien/daysandbox_bot)
You can contact author of the bot at @madspectator
"""

def save_event(event_type, msg, db):
    db.event.save({
        'type': event_type,
        'chat_id': msg.chat.id,
        'chat_username': msg.chat.username,
        'user_id': msg.from_user.id,
        'username': msg.from_user.username,
        'date': datetime.utcnow(),
        'text': msg.text,
        'forward_from_id': (msg.forward_from.id if msg.forward_from else None),
        'forward_from_username': (msg.forward_from.username if msg.forward_from else None),
    })


def create_bot(api_token, db):
    bot = telebot.TeleBot(api_token)

    joined_users = {}
    for user in db.joined_user.find():
        joined_users[(user['chat_id'], user['user_id'])] = user['date']

    @bot.message_handler(content_types=['new_chat_members'])
    def handle_new_chat_member(msg):
        for user in msg.new_chat_members:
            now = datetime.utcnow()
            joined_users[(msg.chat.id, user.id)] = now
            db.joined_user.find_one_and_update(
                {
                    'chat_id': msg.chat.id,
                    'user_id': user.id,
                    'chat_username': msg.chat.username,
                    'user_username': user.username,
                },
                {'$set': {'date': now}},
                upsert=True,
            )

    @bot.message_handler(commands=['start', 'help'])
    def handle_start_help(msg):
        bot.reply_to(msg, HELP, parse_mode='Markdown')

    @bot.message_handler(commands=['stat'])
    def handle_stat(msg):
        days = []
        top_today = Counter()
        top_week = Counter()
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        for x in range(7):
            day = today - timedelta(days=x)
            query = {'$and': [
                {'type': 'delete_msg'},
                {'date': {'$gte': day}},
                {'date': {'$lt': day + timedelta(days=1)}},
            ]}
            num = 0
            for event in db.event.find(query):
                num += 1
                if day == today:
                    top_today[event['chat_username']] += 1
                top_week[event['chat_username']] += 1
            days.insert(0, num)
        ret = 'Recent 7 days: %s' % ' | '.join([str(x) for x in days])
        ret += '\nTop today: %s' % ', '.join('%s (%d)' % x for x in top_today.most_common(5)) 
        ret += '\nTop week: %s' % ', '.join('%s (%d)' % x for x in top_week.most_common(5)) 
        bot.reply_to(msg, ret)


    @bot.message_handler(func=lambda x: True)
    def handle_sticker(msg):
        try:
            join_date = joined_users[(msg.chat.id, msg.from_user.id)]
        except KeyError:
            return
        if datetime.utcnow() - timedelta(hours=24) > join_date:
            return
        to_delete = False
        for ent in (msg.entities or []):
            if ent.type == 'url': 
                to_delete = True
                break
        if not to_delete:
            if msg.forward_from:
                to_delete = True
        if to_delete:
            bot.delete_message(msg.chat.id, msg.message_id)
            save_event('delete_msg', msg, db)

    return bot



def main():
    parser = ArgumentParser()
    parser.add_argument('--mode')
    opts = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG)
    with open('var/config.json') as inp:
        config = json.load(inp)
    if opts.mode == 'test':
        token = config['test_api_token']
    else:
        token = config['api_token']
    db = MongoClient()['daysandbox']
    bot = create_bot(token, db)
    bot.polling()


if __name__ == '__main__':
    main()
