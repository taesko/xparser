import pytest

import xrp.parser
import xrp.views


class TestResources:

    def resources(self, file_path):
        parser = xrp.parser.XParser()
        with open(file_path) as f:
            parser.parse(f.read())
        return xrp.views.ResourcesView.of_parser(parser)

    @pytest.fixture(scope='class')
    def strawberry_resources(self):
        return self.resources('tests/data/res/strawberry')

    @pytest.mark.parametrize('file,filter_string,result_ids', [
        ('tests/data/res/strawberry', '*color0', ['URxvt*color0']),
        ('tests/data/res/strawberry', '*foreground', ['*foreground'])
    ])
    def test_filter(self, file, filter_string, result_ids):
        res = self.resources(file)
        filtered = res.filter(filter_string)
        assert sorted(filtered.keys()) == sorted(result_ids)


class TestEmptyLines:
    @pytest.mark.parametrize('file', [
        'tests/data/res/strawberry'
    ])
    def test_text_at_line(self, file):
        with open(file) as f:
            contents = f.read()
        lines = xrp.views.EmptyLinesView.of_parser(xrp.XParser(contents))
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
