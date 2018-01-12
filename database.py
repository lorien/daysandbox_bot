from pymongo import MongoClient


def connect_db():
    db = MongoClient()['daysandbox']
    db.user.create_index('username', unique=True)
    return db
