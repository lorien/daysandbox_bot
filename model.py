def load_joined_users(db):
    ret = {}
    fields = {'chat_id': 1, 'user_id': 1, 'date': 1, '_id': 0}
    for user in db.joined_user.find({}, fields):
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
