from xrp.views import XFileView
from .parser import XParser


def parse(text):
    """ Parse a string iterable.

    Returns an XFileView object for which the following attributes are accessible:

    `resource` - a str->str mapping of resource identifiers to resource values. If a resource
    value is the name of a definition the value of the definition is returned instead.

    `definitions` - a str->str mapping of definitions of names to their values

    `includes` - a sequence of include statements with 0 based indexing that returns
    the string used in the include.

    `comments` - a sequence of comments with 0 based indexing that returns the comment string

    :rtype: xrp.views.XFileView
    """
    return XFileView(XParser(text_iterable=text))


def parse_file(file, encoding=''):
    """ Reads the file's contents and returns the output of parse(text=contents).
    """
    with open(file, encoding=encoding) as f:
        return parse(f.read())
