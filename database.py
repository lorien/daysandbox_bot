from pymongo import MongoClient


def connect_db():
    db = MongoClient()['daysandbox']
    db.user.create_index('username', unique=True)
    db.joined_user.create_index([('chat_id', 1), ('user_id', 1)])
    db.event.create_index([('type', 1), ('date', 1)])
    db.day_stat.create_index('date')
    return db
