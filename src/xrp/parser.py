import abc
import itertools
import re

import collections

COMMENT_START = '!'
DEFINE_START = '#'
RESOURCE_SEP = ':'
WHITESPACE_CHARS = (' ', '\n')


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
    """ Iterator that can peek N steps ahead through a peek(n) method.

    Initialize with a single iterable argument.
    """
    _exhausted = object()

    def __init__(self, iterable):
        self.iterable = iter(iterable)
        self.character_queue = collections.deque()

    def _advance_iter(self):
        return next(self.iterable, self._exhausted)

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.character_queue) == 0:
            return next(self.iterable)
        else:
            return self.character_queue.popleft()

    def peek(self, n=1):
        """ Peek n steps ahead.

        Raises ValueError if n is not a positive non-zero integer.

        Raises StopIteration if n steps ahead is past the range of the iterable. You can still get
        the characters before step which raises StopIteration (if there are any) by iterating over self.
        """
        if n <= 0:
            raise ValueError("n argument must be a positive non-zero integer, got {} instead".format(n))
        elif n <= len(self.character_queue):
            return self.character_queue[n - 1]
        else:
            needed = n - len(self.character_queue)
            for _ in range(needed):
                self.character_queue.append(next(self.iterable))
            return self.character_queue[n - 1]


def take_line(iterable):
    """ Advances the iterable to the next new line and returns the passed characters as a string.

    The newline character is not included.

    :param iterable: any iterable
    :return: a string of the next line.
    """
    return ''.join(itertools.takewhile(lambda c: c != '\n', iterable))


class XStatement(abc.ABC):
    """ An ABC for parsed statements in an XResources file."""

    @property
    def line(self):
        return self._line

    @classmethod
    @abc.abstractmethod
    def from_iter(cls, iterable, linenum):
        raise NotImplementedError()

    @abc.abstractmethod
    def __str__(self):
        raise NotImplementedError()

    @abc.abstractmethod
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
        # assumes every char but ':' can be part of a resource identifier
        match = re.match(r'([^:]+):(.*)', line)
        if match:
            resource_id = match.group(1).strip()
            resource_val = match.group(2).strip()
            return cls(resource=resource_id, value=resource_val, line=linenum)
        else:
            raise XParseError(f"Incorrect statement '{line}' at line {linenum}")

    def __str__(self):
        return f"{self.resource}{RESOURCE_SEP}{self.value}\n"

    def __repr__(self):
        return f'{self.__class__.__name__}(resource={self.resource}, value={self.value}, line={self.line})'


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
            raise XParseError(f"Incorrect define statement '{line}' at line {linenum}")

    def __str__(self):
        return f'{DEFINE_START}define {self.name} {self.value}\n'

    def __repr__(self):
        return f'{self.__class__.__name__}(name={self.name}, value={self.value}, line={self.line})'


class XCommentStatement(XStatement):

    def __init__(self, comment, line):
        self.comment = comment
        self._line = line

    @classmethod
    def from_iter(cls, iterable, linenum):
        line = take_line(iterable)
        if not line or not line[0] == COMMENT_START:
            raise XParseError(f"Incorrect comment statement '{line}' at line {linenum}")
        return cls(comment=line[1:], line=linenum)

    def __str__(self):
        return f"{COMMENT_START}{self.comment}\n"

    def __repr__(self):
        return f'{self.__class__.__name__}(comment={self.comment}, line={self.line})'


class XIncludeStatement(XStatement):

    def __init__(self, include_file):
        self.file = include_file

    @classmethod
    def from_iter(cls, iterable, linenum):
        line = take_line(iterable)
        match = re.match(pattern=r'#include "(.*)"', string=line)
        return cls(include_file=match.group(1))

    def __str__(self):
        return f'#include "{self.file}"'

    def __repr__(self):
        return f'{self.__class__.__name__}({self.file})'


class Whitespace(XStatement):
    def __init__(self, line_string, line):
        if any(c not in WHITESPACE_CHARS for c in line_string):
            raise ValueError(f'line "{line_string}" has non whitespace characters')
        self._line = line
        self.line_string = line_string

    @classmethod
    def from_iter(cls, iterable, linenum):
        assert iterable.peek() in WHITESPACE_CHARS
        try:
            line = take_line(iterable) + '\n'
            return cls(line_string=line, line=linenum)
        except ValueError:
            raise XParseError(f"line '{line}' at {linenum} has non whitespace characters")

    def __str__(self):
        return self.line_string

    def __repr__(self):
        return f'{self.__class__.__name__}(line={self.line})'


class XParser:
    """ Parse an .Xresources syntax to a dict of resource identifiers and assigned values.

    Initialize with none or one optional arugment `text_iterable` which will be
    parsed immediately.

    The `parse` method can be used to parse a string and the `parse_file` method for files.

    After parsing the following attributes hold the parsed data in the form of XStatements:
    `resources` - dict of resource id strings to XResourceStatement values
    `defines` - dict of names as strings to XDefineStatement values
    `includes` - list of XIncludeStatement objects
    `comments` - list of XCommentStatement objects
    `whitespace` - list of Whitespace objects
    `empty_lines` - list of line numbers that were empty (the first line number is considered to be 0)

    Wildcard expressions '?' and '*' are NOT expanded in the resource identifiers.
    """

    def __init__(self, text_iterable=None):
        self.current_line = 0
        self.peek_iter = None
        self.resources = {}
        self.defines = {}
        self.includes = []
        self.comments = []
        self.whitespace = []
        self.empty_lines = []

        if text_iterable:
            self.parse(text_iterable)

    def parse_file(self, file):
        with open(file) as f:
            yield from self.parse(f.read())

    def parse(self, text_iterable):
        """ Parse a string iterable."""
        self.clear()
        self.peek_iter = PeekableIter(text_iterable)
        lines = []
        while True:
            try:
                next_char = self.peek_iter.peek()
            except StopIteration:
                break
            method = self.parse_method_for(next_char)
            value = method()
            lines.append(value)
            self.current_line += 1
        return lines

    def clear(self):
        """ Clear all data in preperation for parsing a new string."""
        self.peek_iter = None
        self.current_line = 0
        self.resources.clear()
        self.defines.clear()
        self.comments.clear()
        self.whitespace.clear()
        self.empty_lines.clear()

    def parse_resource(self):
        st = XResourceStatement.from_iter(self.peek_iter, linenum=self.current_line)
        self.resources[st.resource] = st
        return st

    def parse_comment(self):
        cs = XCommentStatement.from_iter(self.peek_iter, linenum=self.current_line)
        self.comments.append(cs)
        return cs

    def parse_define(self):
        d = XDefineStatement.from_iter(self.peek_iter, linenum=self.current_line)
        self.defines[d.name] = d
        return d

    def parse_include(self):
        i = XIncludeStatement.from_iter(self.peek_iter, linenum=self.current_line)
        self.includes.append(i)

    def parse_white_space(self):
        ws = Whitespace.from_iter(iterable=self.peek_iter, linenum=self.current_line)
        self.empty_lines.append(self.current_line)
        self.whitespace.append(ws)
        return ws

    def parse_method_for(self, next_char):
        if self.peek_iter.peek() == COMMENT_START:
            return self.parse_comment
        elif self.peek_iter.peek() in WHITESPACE_CHARS:
            return self.parse_white_space
        elif self.peek_iter.peek() == '#':
            if self.peek_iter.peek(2) == 'd':
                return self.parse_define
            elif self.peek_iter.peek(2) == 'i':
                return self.parse_include
        else:
            return self.parse_resource
