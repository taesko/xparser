import pytest

from xrp.parser import XParser, XParseError, XCommentStatement, MissingTokenError, XDefineStatement, XResourceStatement


class TestXParser:

    @pytest.fixture(scope='class')
    def parser(self):
        return XParser()

    @pytest.mark.parametrize('string,defines,comments,resources, empty_lines, error', [
        ("""
! configure color scheme

#define black #000000

*foreground: black
""", {'black': '#000000'}, ['! configure color scheme\n'], {'*foreground': 'black'}, [2, 4], None)
    ])
    def test_parse(self, string, defines, comments, resources, empty_lines, error):
        parser = XParser()
        if error:
            with pytest.raises(error):
                parser.parse(string)
        else:
            parser.parse(string)
            for resource, val in resources.items():
                assert val == parser.resources[resource].value
            for name, val in defines.items():
                assert val == parser.defines[name].value
            assert comments == [str(c) for c in parser.comments]
            string_by_line = string.split('\n')
            for line_num in empty_lines:
                assert string_by_line[line_num].strip() == ''

    def test_parse_file(self):
        import tests.data.parsed.strawberry as sw
        with open('tests/data/res/strawberry', mode='r') as f:
            file_string = f.read()
        parser = XParser()
        parser.parse(file_string)
        for resource_id, resource in parser.resources.items():
            assert resource.value == sw.statements[resource_id]
        for name, define_statement in parser.defines.items():
            assert define_statement.value == sw.defines[name]
        for line_num, line_string in enumerate(file_string.splitlines()):
            if not line_string:
                assert line_num in parser.empty_lines

    def test_clear(self):
        pass

    @pytest.mark.parametrize('string, result, error', [
        ("""
color0: yellow
color1: #00FF00
""", {'color0': 'yellow', 'color1': '#00FF00'}, None),
        ("""
*background: #FFFFFF
incorrect statement""", {}, XParseError)
    ])
    def test_parse_statement(self, string, result, error):
        parser = XParser()
        if error:
            with pytest.raises(error):
                parser.parse(string)
        else:
            parser.parse(string)
            for resource, val in result.items():
                assert val == parser.resources[resource].value

    @pytest.mark.parametrize('string,result,error', [
        ("""
!#define commented out
!pew pew pew
!*color0 = out""", ['!#define commented out\n', '!pew pew pew\n', '!*color0 = out\n'], None),
        (""" ! bad comment""", [], XParseError)
    ])
    def test_parse_comment(self, string, result, error):
        parser = XParser()
        if error:
            with pytest.raises(error):
                parser.parse(string)
        else:
            parser.parse(string)
            assert result == [str(c) for c in parser.comments]

    @pytest.mark.parametrize('string,result,error', [
        ("""
#define color0 #00FF00
#define color1 yellow
""",
         {'color0': '#00FF00', 'color1': 'yellow'}, None),
        ("""
#define color
#define color1 blue
""",
         {}, XParseError)
    ])
    def test_parse_define(self, string, result, error):
        parser = XParser()
        if error:
            with pytest.raises(error):
                parser.parse(string)
        else:
            parser.parse(string)
            for name, val in result.items():
                assert val == parser.defines[name].value


class TestXComment:
    @pytest.mark.parametrize('string,error', [
        ("!comment at the start of the line\n", None),
        ("#define smth value !incorrect comment at the end\n", MissingTokenError),
        ("missing exclamation char\n", MissingTokenError),
        ("\n!comment after a newline shouldn't be parsed\n", MissingTokenError),
        ("!comment with missing newline char should get parsed because it mightt be the last line", None)
    ])
    def test_from_iter(self, string, error):
        line = 0
        if error:
            with pytest.raises(error):
                XCommentStatement.from_iter(string, line)
        else:
            expected = string
            xc = XCommentStatement.from_iter(string, line)
            if string.startswith('!'):
                expected = expected[1:]
            if string.endswith('\n'):
                expected = expected[:-1]
            assert expected == xc.comment


class TestXDefine:

    @pytest.mark.parametrize('string,error', [
        ('#define red #FF0000\n', None),
        ('define green #00FF00\n', XParseError),
        ('#define pink\n', XParseError),
        ('#nodefine blue #0000FF\n', XParseError)
    ])
    def test_from_iter(self, string, error):
        linenum = 0
        if error:
            with pytest.raises(error):
                XDefineStatement.from_iter(string, linenum)
        else:
            expected = string
            xd = XDefineStatement.from_iter(string, linenum)
            assert expected == str(xd)


class TestXStatement:
    @pytest.mark.parametrize('string, error', [
        ('*color0: pink', None),
        ('*color = pink', XParseError),
        ('*color0 : pink', None),
        ('*color=pink', XParseError)
    ])
    def test_from_iter(self, string, error):
        linenum = 0
        if error:
            with pytest.raises(error):
                XResourceStatement.from_iter(string, linenum)
        else:
            expected = string
            xs = XResourceStatement.from_iter(iterable=string, linenum=linenum)
            return expected == str(xs)
