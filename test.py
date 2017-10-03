from util import find_username_links, find_external_links, fetch_user_type


def test_link_finders():
    rows = [
        'foobar @foobar @ foobar',
        'test ya.ru http://dumpz.org',
        ' :))) russia.ru/foo/bar?ar=яяя; test dumpz.org ',
    ]
    for row in rows:
        print('Input: %s' % row)
        print('usernames: ', find_username_links(row))
        print('urls: ', find_external_links(row))


def test_fetch_user_type():
    config = (
        ('itforge', 'group'),
        ('madspectator', 'user'),
        ('PimenTechnical', 'channel'),
    )
    for username, type_ in config:
        ret = fetch_user_type(username)
        print(username, ret)
        assert  ret == type_


def main():
    test_link_finders()
    test_fetch_user_type()


if __name__ == '__main__':
    main()
