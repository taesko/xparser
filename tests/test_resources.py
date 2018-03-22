import pytest

import xrp.resources


class Test_MatchResource:

    @pytest.mark.parametrize('resource_id,components', [
        ('*color0', ['*', 'color0']),
        ('?.color0', ['?', 'color0']),
        ('URxvt*foreground', ['URxvt', '*', 'foreground']),
        ('comp_a.*.comp_d.attribute', ['comp_a', '*', 'comp_d', 'attribute'])
    ])
    def test_components(self, resource_id, components):
        assert xrp.resources._MatchResource.components(resource_id) == components

    @pytest.mark.parametrize('components,padded', [
        (['comp_a', '*', 'comp_d', 'attribute'], ['comp_a', '?', 'comp_d', 'attribute']),
        (['*', 'color0'], ['?', '?', '?', 'color0'])
    ])
    def test_pad_components(self, components, padded):
        assert xrp.resources._MatchResource.pad_components(components) == padded

    @pytest.mark.parametrize('comp_1,comp_2,result', [
        ('URXvt', '?', True),
        ('?', 'color0', True),
        ('URxvt', 'color0', False),
        ('color0', 'color0', True)
    ])
    def test_compare_component(self, comp_1, comp_2, result):
        assert xrp.resources._MatchResource.compare_component(comp_1, comp_2) == result

    @pytest.mark.parametrize('resource_id,string,result', [
        ("comp_a.*.comp_d.attribute", "comp_a.*.attribute", True),
        ("comp_a.comp_b.*.attribute", "comp_a.comp_b.*.comp_d.attribute", True),
        ("comp_a.?.?.comp_d.attribute", "comp_a.*.attribute", True)
    ])
    def test_compare(self, resource_id, string, result):
        mr = xrp.resources._MatchResource(resource_id, string)
        assert mr.compare() == result
