import pytest

import xrp.parser
import xrp.views


class TestResources:

    def get_file_view(self, file_path):
        with open(file_path) as f:
            return self.get_string_view(f.read())

    @staticmethod
    def get_string_view(string):
        parser = xrp.parser.XParser()
        parser.parse(string)
        return xrp.views.ResourcesView(resource_statements=parser.resources,
                                       def_ctx=xrp.views.DefinitionsView(parser.defines))

    @pytest.fixture(scope='class')
    def strawberry_resources(self):
        return self.get_file_view('tests/data/res/strawberry')

    @pytest.mark.parametrize('file,filter_string,result_ids', [
        ('tests/data/res/strawberry', '*color0', ['URxvt*color0']),
        ('tests/data/res/strawberry', '*foreground', ['*foreground'])
    ])
    def test_filter(self, file, filter_string, result_ids):
        res = self.get_file_view(file)
        filtered = res.filter(filter_string)
        assert sorted(filtered.keys()) == sorted(result_ids)

    @pytest.mark.parametrize('input_,expected', [
        (
"""#define white #FFFFFF
#define hotpink #FF69b4
*color0: white
*color1: hotpink
""",
{'*color0': '#FFFFFF', '*color1': '#FF69b4'}
        )
    ])
    def test_defined(self, input_, expected):
        res = self.get_string_view(input_)
        for res_id, res_val in expected.items():
            assert res[res_id] == res_val


class TestEmptyLines:
    @pytest.mark.parametrize('file', [
        'tests/data/res/strawberry'
    ])
    def test_text_at_line(self, file):
        with open(file) as f:
            contents = f.read()
        x_parser = xrp.XParser(contents)
        lines = xrp.views.EmptyLinesView(whitespace_list=x_parser.whitespace,
                                         empty_lines=x_parser.empty_lines)
        file_lines = contents.splitlines()
        empty_lines = [file_line_num for file_line_num, line_string in enumerate(file_lines) if not line_string.strip()]
        assert sorted(lines) == sorted(empty_lines)


class TestXFileView:
    @pytest.fixture(scope='class')
    def contents(self):
        with open('tests/data/res/strawberry') as f:
            return f.read()

    @pytest.fixture(scope='class')
    def xfileview(self, contents):
        return xrp.views.XFileView(xrp.XParser(contents))

    def test_text_at_line(self, xfileview, contents):
        for line_num, line_string in enumerate(contents.splitlines()):
            if 'define' in line_string:
                line_string = line_string.replace('  ', ' ')
            elif ':' in line_string:
                line_string = line_string.replace(' ', '')
            assert xfileview.text_at_line(line_num) == line_string + '\n'

    def test_full_text(self):
        pass
