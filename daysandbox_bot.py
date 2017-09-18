#!/usr/bin/env python
import re
from collections import Counter
import jsondate
import json
import logging
import telebot
from argparse import ArgumentParser
from pymongo import MongoClient
from datetime import datetime, timedelta
import html

from util import find_username_links, find_external_links

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
/set publog=[yes|no] - enable/disable messages to group about deleted posts

*How to log deleted messages to private channel*
Add bot to the channel as admin. Write "/setlog" to the channel. Forward message to the group.
Write /unsetlog in the group to disable logging to channel.

*Questions, Feedback*
Support group: [@daysandbox_chat](https://t.me/daysandbox_chat)

*Open Source*

The source code is available at [github.com/lorien/daysandbox_bot](https://github.com/lorien/daysandbox_bot)
"""
SUPERUSER_IDS = set([
    46284539, # @madspectator
])
GROUP_SETTING_KEYS = ('publog', 'log_channel_id')
GLOBAL_CHANNEL_ID = -1001148916224 

def dump_message(msg):
    return {
        'chat_id': msg.chat.id,
        'chat_username': msg.chat.username,
        'user_id': msg.from_user.id,
        'user_username': msg.from_user.username,
        'date': datetime.utcnow(),
        'text': msg.text,
        'forward_from_id': (msg.forward_from.id if msg.forward_from else None),
        'forward_from_username': (msg.forward_from.username if msg.forward_from else None),
    }


def check_members_username(datab, username):
    if datab.joined_user.findOne({'user_username': username}):
        return True


def save_event(db, event_type, msg, **kwargs):
    event = dump_message(msg)
    event.update({
        'type': event_type,
    })
    event.update(**kwargs)
    db.event.save(event)


def load_joined_users(db):
    ret = {}
    for user in db.joined_user.find():
        ret[(user['chat_id'], user['user_id'])] = user['date']
    return ret


def load_group_config(db):
    ret = {}
    for item in db.config.find():
        key = (
            item['group_id'],
            item['key'],
        )
        ret[key] = item['value']
    return ret


def set_setting(db, group_config, group_id, key, val):
    assert key in GROUP_SETTING_KEYS
    db.config.find_one_and_update(
        {
            'group_id': group_id,
            'key': key,
        },
        {'$set': {'value': val}},
        upsert=True,
    )
    group_config[(group_id, key)] = val


def get_setting(group_config, group_id, key, default=None):
    assert key in GROUP_SETTING_KEYS
    try:
        return group_config[(group_id, key)]
    except KeyError:
        return default


def create_bot(api_token, db):
    bot = telebot.TeleBot(api_token)
    joined_users = load_joined_users(db)
    group_config = load_group_config(db)
    delete_events = {}

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
        if msg.chat.type != 'private':
            return
        bot.reply_to(msg, HELP, parse_mode='Markdown')

    @bot.message_handler(commands=['stat'])
    def handle_stat(msg):
        if msg.chat.type != 'private':
            return
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
                key  = (
                    '@%s' % event['chat_username'] if event['chat_username']
                    else '#%d' % event['chat_id']
                )
                if day == today:
                    top_today[key] += 1
                top_week[key] += 1
            days.insert(0, num)
        ret = 'Recent 7 days: %s' % ' | '.join([str(x) for x in days])
        ret += '\n\nTop today:\n%s' % '\n'.join('  %s (%d)' % x for x in top_today.most_common(10)) 
        ret += '\n\nTop week:\n%s' % '\n'.join('  %s (%d)' % x for x in top_week.most_common(10)) 
        bot.reply_to(msg, ret)

    @bot.message_handler(commands=['set', 'get'])
    def handle_set_get(msg):
        if not msg.chat.type in ('group', 'supergroup'):
            bot.reply_to(msg, 'This command have to be called from the group')
            return
        re_cmd_set = re.compile(r'^/set (publog)=(.+)$')
        re_cmd_get = re.compile(r'^/get (publog)()$')
        if msg.text.startswith('/set'):
            match = re_cmd_set.match(msg.text)
            action = 'set'
        else:
            match = re_cmd_get.match(msg.text)
            action = 'get'
        if not match:
            bot.reply_to(msg, 'Invalid arguments') 
            return

        key, val = match.groups()

        admins = bot.get_chat_administrators(msg.chat.id)
        admin_ids = set([x.user.id for x in admins]) | set(SUPERUSER_IDS)
        if msg.from_user.id not in admin_ids:
            bot.reply_to(msg, 'Access denied')
            return

        if action == 'get':
            bot.reply_to(msg, str(get_setting(group_config, msg.chat.id, key)))
        else:
            if key == 'publog':
                if val in ('yes', 'no'):
                    val_bool = (val == 'yes')
                    set_setting(db, group_config, msg.chat.id, key, val_bool)
                    bot.reply_to(msg, 'Set public_notification to %s for group %s' % (
                        val_bool,
                        '@%s' % msg.chat.username if msg.chat.username else '#%d' % msg.chat.id,
                    ))
                else:
                    bot.reply_to(msg, 'Invalid public_notification value. Should be: yes or no')
            else:
                bot.reply_to(msg, 'Unknown action: %s' % key)

    @bot.message_handler(commands=['setlog'])
    def handle_setlog(msg):
        if not msg.chat.type in ('group', 'supergroup'):
            bot.reply_to(msg, 'This command have to be called from the group')
            return
        if msg.forward_from_chat.type != 'channel':
            bot.reply_to(msg, 'Command /setlog must be forwarded from channel')
            return
        channel = msg.forward_from_chat

        channel_admin_ids = [x.user.id for x in bot.get_chat_administrators(channel.id)]
        if bot.get_me().id not in channel_admin_ids:
            bot.reply_to(msg, 'I need to be an admin in log channel')
            return

        admins = bot.get_chat_administrators(msg.chat.id)
        admin_ids = set([x.user.id for x in admins]) | set(SUPERUSER_IDS)
        if msg.from_user.id not in admin_ids:
            bot.reply_to(msg, 'Access denied')
            return

        set_setting(db, group_config, msg.chat.id, 'log_channel_id', channel.id)
        tgid = '@%s' % msg.chat.username if msg.chat.username else '#%d' % msg.chat.id
        bot.reply_to(msg, 'Set log channel for group %s' % tgid)

    @bot.message_handler(commands=['unsetlog'])
    def handle_setlog(msg):
        if not msg.chat.type in ('group', 'supergroup'):
            bot.reply_to(msg, 'This command have to be called from the group')
            return

        admins = bot.get_chat_administrators(msg.chat.id)
        admin_ids = set([x.user.id for x in admins]) | set(SUPERUSER_IDS)
        if msg.from_user.id not in admin_ids:
            bot.reply_to(msg, 'Access denied')
            return

        set_setting(db, group_config, msg.chat.id, 'log_channel_id', None)
        tgid = '@%s' % msg.chat.username if msg.chat.username else '#%d' % msg.chat.id
        bot.reply_to(msg, 'Unset log channel for group %s' % tgid)

    @bot.edited_message_handler(
        func=lambda x: True,
        content_types=['text', 'photo', 'video', 'audio', 'sticker', 'document']
    )
    @bot.message_handler(
        func=lambda x: True,
        content_types=['text', 'photo', 'video', 'audio', 'sticker', 'document']
    )
    def handle_any_msg(msg):
        to_delete = False
        if msg.from_user.username == 'madspectator' and msg.text == 'del':
            reason = 'debug delete'
            to_delete = True
        if not to_delete:
            try:
                join_date = joined_users[(msg.chat.id, msg.from_user.id)]
            except KeyError:
                return
            if datetime.utcnow() - timedelta(hours=24) > join_date:
                return
        for ent in (msg.entities or []):
            if ent.type in ('url', 'text_link'):
                to_delete = True
                reason = 'external link'
                break
            if ent.type == 'mention' and not \
                    check_members_username(db, msg.text[(ent.offset + 1):(ent.offset + 1) + (ent.offset - 1)]):
                to_delete = True
                reason = 'link to @username'
                break
        if not to_delete:
            if msg.forward_from or msg.forward_from_chat:
                reason = 'forwarded'
                to_delete = True
        if not to_delete:
            if find_username_links(msg.caption or ''):
                reason = 'caption @username link'
                to_delete = True
        if not to_delete:
            if find_external_links(msg.caption or ''):
                reason = 'caption external link'
                to_delete = True
        if to_delete:
            bot.delete_message(msg.chat.id, msg.message_id)
            save_event(db, 'delete_msg', msg, reason=reason)
            if msg.from_user.first_name and msg.from_user.last_name:
                from_user = '%s %s' % (
                    msg.from_user.first_name,
                    msg.from_user.last_name,
                )
            elif msg.from_user.first_name:
                from_user = msg.from_user.first_name
            elif msg.from_user.username:
                from_user = msg.from_user.first_name
            else:
                from_user = '#%d' % msg.from_user.id
            event_key = (msg.chat.id, msg.from_user.id)
            if get_setting(group_config, msg.chat.id, 'publog', True):
                # Notify about spam from same user only one time per hour
                if (
                        event_key not in delete_events
                        or delete_events[event_key] < datetime.utcnow() - timedelta(hours=1)
                    ):
                    ret = 'Removed msg from %s. Reason: new user + %s' % (from_user, reason)
                    bot.send_message(msg.chat.id, ret, parse_mode='HTML')
            delete_events[event_key] = datetime.utcnow()

            ids = set([GLOBAL_CHANNEL_ID])
            channel_id = get_setting(group_config, msg.chat.id, 'log_channel_id')
            if channel_id:
                ids.add(channel_id)
            for chid in ids:
                try:
                    msg_dump = dump_message(msg)
                    msg_dump['reason'] = reason
                    dump = jsondate.dumps(msg_dump, indent=4, ensure_ascii=False)
                    dump = html.escape(dump)
                    from_chat = (
                        '@%s' % msg.chat.username if msg.chat.username
                        else '#%d' % msg.chat.id
                    )
                    bot.send_message(
                        chid,
                        'Message deleted from %s\n<pre>%s</pre>' % (from_chat, dump),
                        parse_mode='HTML'
                    )
                except Exception as ex:
                    logging.error(
                        'Failed to send notification to channel [%d]' % chid,
                        exc_info=ex
                    )

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
