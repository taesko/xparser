import abc
import itertools

import collections

from xrp.match import match_resource


class BaseView(abc.ABC):

    @property
    @abc.abstractmethod
    def x_statements(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def x_statement(self, *args, **kwargs):
        raise NotImplementedError()

    def statement_at_line(self, line_num):
        for x_state in self.x_statements:
            if line_num == x_state.line:
                return x_state
        else:
            raise IndexError("line {} is not in this view".format(line_num))

    def text_at_line(self, line_num):
        return str(self.statement_at_line(line_num))


class BaseDictView(BaseView, collections.Mapping):
    @property
    @abc.abstractmethod
    def dict_data(self):
        raise NotImplementedError()

    @property
    def x_statements(self):
        return self.dict_data.values()

    def x_statement(self, key):
        return self.dict_data[key]

    def __len__(self):
        return len(self.dict_data)

    def __iter__(self):
        for key in self.dict_data:
            yield key


class ResourcesView(BaseDictView):
    """ An immutable mapping of resource identifiers to resource values.

    Initialize by providing a dict/mapping of resource identifiers to
    parsed resource statements and a dict/mapping of defined names to their values.
    Strings are expected as the keys and values (except for resource statements).

    This is a subclass of collections.Mapping and as such the common
    dictionary interface and methods are implemented (__getitem__, __len__, .keys(),
    .values(), .items(), etc.). The keys and values of this object are always strings.

    The raw resource statements data is accessible through the `dict_data` property.
    Modifying that object will be reflected in this class as this is a view of the object.

    You can filter the view through regex with the use of the `filter` method which
    returns a new object of the same class, but with only those resources who's identifier
    matched the string. See xrp.match.match_resource for more details.
    """

    def __init__(self, resource_statements, def_ctx):
        self.resource_statements = resource_statements
        self.definition_ctx = def_ctx

    @property
    def dict_data(self):
        return self.resource_statements

    def __getitem__(self, key):
        raw_val = self.x_statement(key).value
        return self.definition_ctx.get(raw_val, raw_val)

    def filter(self, string):
        resources = {}
        for res_id in self:
            if match_resource(resource=res_id, pattern=string):
                resources[res_id] = self.x_statement(res_id)
        return self.__class__(resource_statements=resources, def_ctx=self.definition_ctx)


class DefinitionsView(BaseDictView):
    """ A mapping of definition names to defined values.

    Initialize with a single argument `define_statements` that is
    a dict/mapping from names to parsed define statements. The keys are expected
    to be strings.

    Interface is similar to that of ResourcesView.
    """
    def __init__(self, define_statements):
        self.define_statements = define_statements

    @property
    def dict_data(self):
        return self.define_statements

    def __getitem__(self, key):
        return self.define_statements[key].value


class IncludedView(BaseView, collections.Sequence):
    """ A sequence of included files.

    Initialize with a single argument of a list of include statements.

    This is a subclass of collections.Sequence as such the common
    list interface and methods are implemented (__getitem__, __len__, etc.)
    Indexing is 0 based and the return values of __getitem__ are always the strings
    used in the include statement. They ARE NOT absolute paths to the included file
    as those depend on the preprocessor arguments.
    """

    def __init__(self, include_statements):
        self.include_statements = include_statements

    @property
    def x_statements(self):
        return self.include_statements

    def x_statement(self, line):
        for i in self.include_statements:
            if i.line == line:
                return i

    def __getitem__(self, i) -> str:
        return self.include_statements[i].file

    def __len__(self) -> int:
        return len(self.include_statements)


class CommentsView(BaseView, collections.Sequence):
    """ A sequence of comments. Interface is similar to IncludedView.

    Initialize with a list of comment statements.
    """

    def __init__(self, comment_statements):
        self.comment_statements = comment_statements

    @property
    def x_statements(self):
        return self.comment_statements

    def x_statement(self, line):
        return self.comment_statements[line]

    def __getitem__(self, key):
        return self.comment_statements[key].value

    def __len__(self):
        return len(self.comment_statements)


class EmptyLinesView(BaseView, collections.Sequence):
    """ A sequence of lines without any non-whitespace characters.

    Empty lines are considered lines without any non-whitespace characters.

    Initialize with two arguments - a list of whitespace objects from xrp.parse
    and a list of empty line objects from the same module.

    Interface is similar to that of other sequence views.
    """

    def __init__(self, whitespace_list, empty_lines):
        self.whitespace_list = whitespace_list
        self.empty_lines = empty_lines
        assert self.empty_lines == [ws.line for ws in self.whitespace_list]

    @property
    def x_statements(self):
        return self.whitespace_list

    def x_statement(self, index):
        """ Return the parsed Whitespace object of the n-th empty line"""
        return self.whitespace_list[index]

    def __getitem__(self, n):
        """ Return the line number of the n-th empty line."""
        return self.empty_lines[n]

    def __len__(self):
        """ Return the number of empty lines"""
        assert len(self.whitespace_list) == len(self.empty_lines)
        return len(self.whitespace_list)


class XFileView(BaseView, collections.Sequence):
    """ A line by line sequence of the parsed file."""
    def __init__(self, parser):
        self.included = IncludedView(include_statements=parser.includes)
        self.definitions = DefinitionsView(define_statements=parser.defines)
        self.resources = ResourcesView(resource_statements=parser.resources, def_ctx=self.definitions)
        self.comments = CommentsView(comment_statements=parser.comments)
        self.whitespace = EmptyLinesView(whitespace_list=parser.whitespace, empty_lines=parser.empty_lines)
        self.line_count = parser.current_line + 1  # parser counts from 0
        self.views = [self.resources, self.definitions, self.included, self.comments, self.whitespace]

    @property
    def x_statements(self):
        """ Return a chain of parsed XStatements."""
        parts = (view.x_statements for view in self.views)
        return itertools.chain(*parts)

    def x_statement(self, line_num):
        """ Return the XStatement at :line_num:."""
        for view in self.views:
            try:
                return view.statement_at_line(line_num)
            except IndexError:
                pass
        else:
            raise IndexError(f"no parsed XStatement at line {line_num}")

    def __getitem__(self, line):
        """ Return XStatement at line"""
        return self.x_statement(line_num=line)

    def __len__(self):
        """ Return number of parsed lines."""
        return self.line_count

    def text_at_line(self, line_num):
        """ Return string of the text at :line_num:."""
        for view in self.views:
            try:
                return view.text_at_line(line_num=line_num)
            except IndexError:
                pass
        else:
            raise IndexError(
                "line {} is not in {} perhaps the parsed file was smaller".format(line_num, self.__class__.__name__))

    def full_text(self):
        """ Rebuild the string from it's parsed XStatements."""
        lines = []
        for line_num in itertools.count():
            try:
                lines.append(self.text_at_line(line_num))
            except IndexError:
                break
        return ''.join(map(str, lines))
