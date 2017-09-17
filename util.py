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
