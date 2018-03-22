from .parser import XParser
from xrp.views import XFileView


def parse(text):
    return XFileView.from_parser(XParser(text_iterable=text))


def parse_file(file):
    with open(file) as f:
        return parse(f.read())
