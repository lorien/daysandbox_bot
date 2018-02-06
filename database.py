from pymongo import MongoClient


def connect_db():
    db = MongoClient()['daysandbox']
    db.user.create_index('username', unique=True)
    db.event.create_index([('type', 1), ('date', 1)])
    return db
