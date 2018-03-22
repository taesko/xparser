import re
import itertools


COMMENT_START = '!'
DEFINE_START = '#'
RESOURCE_SEP = ':'


class XParseError(Exception):
    pass


class MissingTokenError(XParseError):
    def __init__(self, token, line=None):
        msg = f'missing token "{token}"'
        if line:
            msg += f'at line {line}'
        super().__init__(msg)
        self.token = token
        self.line = line


class UnexpectedTokenError(XParseError):

    def __init__(self, token, line=None):
        msg = f'found an inexpected "{token}"'
        if line:
            msg += f'at line {line}'
        super().__init__(msg)
        self.token = token
        self.line = line


class PosIter:
    line_sep = '\n'

    def __init__(self, text_iterable):
        self.iterable = iter(text_iterable)
        self.line = 0
        self.column = 0
        self.was_on_newline = False

    def advance_line(self):
        self.line += 1
        self.column = 0

    def advance_column(self):
        self.column += 1

    def __iter__(self):
        return self

    def __next__(self):
        character = next(self.iterable)
        if character != self.line_sep and self.was_on_newline:
            # the last character was a newline so we advance only the line to get to column 0 for the current character
            self.advance_line()
        else:
            # advance the column for all characters including newline
            self.advance_column()
        if character == self.line_sep:
            self.was_on_newline = True
        return character


class PeekableIter:
    _exhausted = object()

    def __init__(self, iterable):
        self.iterable = iter(iterable)
        self.next_char = self._advance_iter()

    def _advance_iter(self):
        return next(self.iterable, self._exhausted)

    def __iter__(self):
        return self

    def __next__(self):
        return_val = self.next_char
        if return_val == self._exhausted:
            raise StopIteration()
        else:
            self.next_char = self._advance_iter()
            return return_val

    def peek(self):
        if self.next_char == self._exhausted:
            raise StopIteration()
        else:
            return self.next_char


def take_line(iterable):
    return ''.join(itertools.takewhile(lambda c: c != '\n', iterable))


class XStatement:
    def __init__(self, resource, value, line):
        self.resource = resource
        self.value = value
        self.line = line

    @classmethod
    def from_iter(cls, iterable, linenum):
        iterable = iter(iterable)
        line = take_line(iterable)
        match = re.match(r'([ \w*.]+):(.*)', line)
        if match:
            resource_id = match.group(1).strip()
            resource_val = match.group(2).strip()
            return cls(resource=resource_id, value=resource_val, line=linenum)
        else:
            raise XParseError(f"Incorrect statement at line {linenum}")

    def __str__(self):
        return f"{self.resource}{RESOURCE_SEP}{self.value}\n"

    def __repr__(self):
        return f'{self.__class__.__name__}(resource={self.resource}, value={self.value}, line={self.line}'


class XDefine:

    def __init__(self, name, value, line):
        self.name = name
        self.value = value
        self.line = line

    @classmethod
    def from_iter(cls, iterable, linenum):
        line = take_line(iterable)
        match = re.match(r'#define (\w+) (.*)', line)
        if match:
            name = match.group(1)
            value = match.group(2)
            return cls(name=name, value=value, line=linenum)
        else:
            raise XParseError(f"Incorrect define statement at line {linenum}")

    def __str__(self):
        return f'{DEFINE_START}define {self.name} {self.value}\n'

    def __repr__(self):
        return f'{self.__class__.__name__}(name={self.name}, value={self.value}, line={self.line}'


class XComment:

    def __init__(self, comment, line):
        self.comment = comment
        self.line = line

    @classmethod
    def from_iter(cls, iterable, line):
        iterable = iter(iterable)
        if not next(iterable) == COMMENT_START:
            raise MissingTokenError(token=COMMENT_START, line=line)
        return cls(comment=take_line(iterable), line=line)

    def __str__(self):
        return f"{COMMENT_START}{self.comment}\n"

    def __repr__(self):
        return f'{self.__class__.__name__}(comment={self.comment}, line={self.line}'


class XParser:
    """ Parse an .Xresources file iterable to a dict of resource identifiers and assigned values.

    Wildcard expressions '?' and '*' are NOT expanded in the resource identifiers.
    """

    def __init__(self, text_iterable=None):
        self.pos_iter = None
        self.peek_iter = None
        self.resources = {}
        self.defines = {}
        self.comments = []
        self.resources = {}
        if text_iterable:
            self.parse(text_iterable)

    def parse(self, text_iterable):
        self.clear()
        self.pos_iter = PosIter(text_iterable)
        self.peek_iter = PeekableIter(self.pos_iter)
        while True:
            try:
                next_char = self.peek_iter.peek()
            except StopIteration:
                break
            if next_char == DEFINE_START:
                self.parse_define()
            elif next_char == COMMENT_START:
                self.parse_comment()
            elif next_char in ('\n', ' '):
                next(self.peek_iter)  # advance the iterable and skip the newline
                continue
            else:
                self.parse_statement()

    def clear(self):
        self.pos_iter = None
        self.peek_iter = None
        self.resources.clear()
        self.defines.clear()
        self.comments.clear()
        self.resources.clear()

    def parse_statement(self):
        st = XStatement.from_iter(self.peek_iter, linenum=self.pos_iter.line)
        self.resources[st.resource] = st

    def parse_comment(self):
        self.comments.append(XComment.from_iter(self.peek_iter, line=self.pos_iter.line))

    def parse_define(self):
        d = XDefine.from_iter(self.peek_iter, linenum=self.pos_iter.line)
        self.defines[d.name] = d
