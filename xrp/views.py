import collections
import functools

import itertools

from xrp.match import match_resource


def get_base_view(collection):
    class BaseView(collection):
        is_initialized = False

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.is_initialized = True

        @property
        def x_statements(self):
            return self.data

        @classmethod
        def from_parser(cls, parser):
            raise NotImplementedError()

        def text_at_line(self, line_num):
            for x_state in self.iterate_statements():
                if line_num == x_state.line:
                    return str(x_state)
            else:
                raise IndexError("line {} is not in this view".format(line_num))

        def iterate_statements(self):
            raise NotImplementedError()

        def __getitem__(self, item):
            return super().__getitem__(item).value

        def __setitem__(self, key, value):
            if not self.is_initialized:
                super().__setitem__(key, value)
            else:
                raise TypeError("{} object does not support item assignment".format(self.__class__.__name__))

        def __delitem__(self, key):
            if not self.is_initialized:
                super().__delitem__(key=key)
            else:
                raise TypeError("{} object does not support item deletion".format(self.__class__.__name__))

    return BaseView


class BaseDictView(get_base_view(collections.UserDict)):

    @classmethod
    def from_parser(cls, parser):
        raise NotImplementedError()

    def iterate_statements(self):
        return self.x_statements.values()


class BaseListView(get_base_view(collections.UserList)):
    @classmethod
    def from_parser(cls, parser):
        raise NotImplementedError()

    def iterate_statements(self):
        return self.x_statements


class Resources(BaseDictView):

    @classmethod
    def from_parser(cls, parser):
        return cls(parser.resources)

    def filter(self, string):
        resources = {}
        for res_id, value in self.x_statements.items():
            if match_resource(resource=res_id, string=string):
                resources[res_id] = value
        return self.__class__(resources)


class Definitions(BaseDictView):
    @classmethod
    def from_parser(cls, parser):
        return cls(parser.defines)


class Comments(BaseListView):
    @classmethod
    def from_parser(cls, parser):
        return cls(parser.comments)


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
