from urllib.request import urlopen
from urllib.parse import quote
import re

RE_USERNAME = re.compile(r'@[a-z][_a-z0-9]{4,30}', re.I)
RE_SIMPLE_LINK = re.compile(
    r'(?:https?://)?'
    r'[a-z][_.a-z0-9]+\.[a-z]{2,10}'
    r'(?:[^ ]+)?',
    re.X | re.I | re.U
)


def find_username_links(text):
    return RE_USERNAME.findall(text)


def find_external_links(text):
    return RE_SIMPLE_LINK.findall(text)


def fetch_user_type(username):
    url = 'https://t.me/%s' % quote(username)
    try:
        data = urlopen(url, timeout=2).read().decode('utf-8')
    except OSError:
        logging.exception('Failed to fetch URL: %s' % url)
        return None
    else:
        if '>View Group<' in data:
            return 'group'
        elif '>Send Message<' in data:
            return 'user'
        elif '>View Channel<' in data:
            return 'channel'
        else:
            logging.error('Could not detect user type: %s' % url)
