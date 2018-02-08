from collections import Counter
from datetime import datetime, timedelta

from database import connect_db


def setup_arg_parser(parser):
    parser.add_argument('days_ago', type=int, default=0)



def get_chat_id(event):
    return event.get('chat_id', event['chat']['id'])


def main(days_ago, **kwargs):
    db = connect_db()
    day = datetime.utcnow().replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    for x in range(days_ago + 1):
        start = day - timedelta(days=x)
        end = start + timedelta(days=1)
        query = {
            'type': 'delete_msg',
            'date': {
                '$gte': start,
                '$lt': end,
            },
        }
        del_count = 0
        chat_reg = set()
        for event in db.event.find(query):
            del_count += 1
            chat_reg.add(get_chat_id(event))
        db.day_stat.find_one_and_update(
            {'date': start},
            {'$set': {
                'delete_msg': del_count,
                'chat': len(chat_reg),
            }},
            upsert=True,
        )
        print('Date: %s' % start)
        print(' * delete_msg: %d' % del_count)
        print(' * chat: %d' % len(chat_reg))
