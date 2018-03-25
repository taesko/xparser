import collections.abc
import abc

import itertools

from xrp.match import match_resource


class BaseView(abc.ABC):

    @classmethod
    @abc.abstractmethod
    def from_parser(cls, parser):
        raise NotImplementedError()

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


class BaseDictView(BaseView, collections.abc.Mapping):
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


class BaseListView(BaseView, collections.abc.Mapping):
    @property
    @abc.abstractmethod
    def list_data(self):
        raise NotImplementedError()

    @property
    def x_statements(self):
        return self.list_data

    def x_statement(self, index):
        return self.list_data[index]

    def __len__(self):
        return len(self.list_data)

    def __iter__(self):
        for index in range(len(self)):
            yield self[index]


class Resources(BaseDictView):

    def __init__(self, resources):
        self.resource_statements = resources

    @property
    def dict_data(self):
        return self.resource_statements

    @classmethod
    def from_parser(cls, parser):
        return cls(parser.resources)

    def __getitem__(self, key):
        return self.resource_statements[key].value

    def filter(self, string):
        resources = {}
        for res_id in self:
            if match_resource(resource=res_id, string=string):
                resources[res_id] = self.x_statement(res_id)
        return self.__class__(resources)


class Definitions(BaseDictView):

    def __init__(self, definitions):
        self.define_statements = definitions

    @classmethod
    def from_parser(cls, parser):
        return cls(parser.defines)

    @property
    def dict_data(self):
        return self.define_statements

    def __getitem__(self, key):
        return self.define_statements[key].value


class Comments(BaseListView):

    def __init__(self, comment_statements):
        self.comment_statements = comment_statements

    @classmethod
    def from_parser(cls, parser):
        return cls(parser.comments)

    @property
    def list_data(self):
        return self.comment_statements

    def __getitem__(self, key):
        return self.comment_statements[key].value


class EmptyLines(collections.UserList):
    @classmethod
    def from_parser(cls, parser):
        return cls(parser.empty_lines)

    def text_at_line(self, line_num):
        if line_num in self:
            return '\n'
        else:
            raise IndexError('line {} is not an empty line'.format(line_num))


class XFileView(collections.namedtuple('ParsedData', ['resources', 'definitions', 'comments', 'whitespace'])):
    @classmethod
    def from_parser(cls, parser):
        return cls(resources=Resources.from_parser(parser),
                   definitions=Definitions.from_parser(parser),
                   comments=Comments.from_parser(parser),
                   whitespace=EmptyLines.from_parser(parser))

    def text_at_line(self, line_num):
        for view in self:
            try:
                return view.text_at_line(line_num=line_num)
            except IndexError:
                pass
        else:
            raise IndexError(
                "line {} is not in {} perhaps the parsed file was smaller".format(line_num, self.__class__.__name__))

    def full_text(self):
        lines = []
        for line_num in itertools.count():
            try:
                lines.append(self.text_at_line(line_num))
            except IndexError:
                break
        return ''.join(map(str, lines))
