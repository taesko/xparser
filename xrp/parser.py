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

    @property
    def line(self):
        return self._line

    @classmethod
    def from_iter(cls, iterable, linenum):
        raise NotImplementedError()

    def __str__(self):
        raise NotImplementedError()

    def __repr__(self):
        raise NotImplementedError()


class XResourceStatement(XStatement):
    def __init__(self, resource, value, line):
        self.resource = resource
        self.value = value
        self._line = line

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


class XDefineStatement(XStatement):

    def __init__(self, name, value, line):
        self.name = name
        self.value = value
        self._line = line

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


class XCommentStatement(XStatement):

    def __init__(self, comment, line):
        self.comment = comment
        self._line = line

    @classmethod
    def from_iter(cls, iterable, linenum):
        iterable = iter(iterable)
        if not next(iterable) == COMMENT_START:
            raise MissingTokenError(token=COMMENT_START, line=linenum)
        return cls(comment=take_line(iterable), line=linenum)

    def __str__(self):
        return f"{COMMENT_START}{self.comment}\n"

    def __repr__(self):
        return f'{self.__class__.__name__}(comment={self.comment}, line={self.line}'


class XParser:
    """ Parse an .Xresources file iterable to a dict of resource identifiers and assigned values.

    Wildcard expressions '?' and '*' are NOT expanded in the resource identifiers.
    """

    def __init__(self, text_iterable=None):
        self.current_line = 0
        self.peek_iter = None
        self.resources = {}
        self.defines = {}
        self.comments = []
        self.empty_lines = []
        if text_iterable:
            self.parse(text_iterable)

    @classmethod
    def from_file(cls, file):
        with open(file) as f:
            cls(f.read())

    def parse_file(self, file):
        with open(file) as f:
            self.parse(f.read())

    def parse(self, text_iterable):
        self.clear()
        self.peek_iter = PeekableIter(text_iterable)
        while True:
            try:
                next_char = self.peek_iter.peek()
            except StopIteration:
                break
            if next_char == DEFINE_START:
                self.parse_define()
                self.current_line += 1
            elif next_char == COMMENT_START:
                self.parse_comment()
                self.current_line += 1
            elif next_char == '\n':
                self.parse_empty_line()
                self.current_line += 1
            elif next_char == ' ':
                self.parse_white_space()
            else:
                self.parse_resource()
                self.current_line += 1

    def clear(self):
        self.peek_iter = None
        self.current_line = 0
        self.resources.clear()
        self.defines.clear()
        self.comments.clear()
        self.resources.clear()

    def parse_resource(self):
        st = XResourceStatement.from_iter(self.peek_iter, linenum=self.current_line)
        self.resources[st.resource] = st

    def parse_comment(self):
        self.comments.append(XCommentStatement.from_iter(self.peek_iter, linenum=self.current_line))

    def parse_define(self):
        d = XDefineStatement.from_iter(self.peek_iter, linenum=self.current_line)
        self.defines[d.name] = d

    def parse_empty_line(self):
        assert next(self.peek_iter) == '\n'
        self.empty_lines.append(self.current_line)

    def parse_white_space(self):
        assert next(self.peek_iter) == ' '

