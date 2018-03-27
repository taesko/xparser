from xrp.views import XFileView
from .parser import XParser


def parse(text):
    return XFileView(XParser(text_iterable=text))


def parse_file(file):
    with open(file) as f:
        return parse(f.read())
