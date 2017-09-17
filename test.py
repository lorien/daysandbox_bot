from util import find_username_links, find_external_links


def main(**kwargs):
    rows = [
        'foobar @foobar @ foobar',
        'test ya.ru http://dumpz.org',
        ' :))) russia.ru/foo/bar?ar=яяя; test dumpz.org ',
    ]
    for row in rows:
        print('Input: %s' % row)
        print('usernames: ', find_username_links(row))
        print('urls: ', find_external_links(row))


if __name__ == '__main__':
    main()
