import itertools

MAX_RESOURCE_COMPONENTS = 4
WILDCARDS = ('*', '?')


class _MatchResource:
    """

    Example usage:
    >>> _MatchResource("comp_a.*.comp_d.attribute", "comp_a.*.attribute").compare() == True
    >>> _MatchResource("comp_a.comp_b.*.attribute", "comp_a.comp_b.*.comp_d.attribute").compare() == True
    >>> _MatchResource("comp_a.?.?.comp_d.attribute", "comp_a.*.attribute").compare() == True
    """

    def __init__(self, resource, string):
        resource_components = self.components(resource)
        string_components = self.components(string)
        pad_len = max(len(resource_components), len(string_components))

        self.resource_components = resource_components
        self.expanded_resource = self.pad_components(resource_components, length=pad_len)

        self.string_components = string_components
        self.expanded_string = self.pad_components(string_components, length=pad_len)

    @staticmethod
    def components(resource_id):
        result = []
        comp = []
        for char in resource_id:
            if char == '.':
                result.append(''.join(comp))
                comp.clear()
            elif char in WILDCARDS:
                result.append(''.join(comp))
                comp.clear()
                result.append(char)
            else:
                comp.append(char)
        result.append(''.join(comp))
        comp.clear()
        result = [ele for ele in result if ele]
        if result[-1] in WILDCARDS:
            raise ValueError("Invalid resource id - a wildcard character cannot be used as an attribute name")
        return result

    @staticmethod
    def pad_components(components, length=MAX_RESOURCE_COMPONENTS):
        expanded_resource = list(components)
        try:
            resource_wild = components.index('*')
            expanded_resource.pop(resource_wild)
            for _ in range(length - len(expanded_resource)):
                expanded_resource.insert(resource_wild, '?')
        except ValueError:
            pass
        return expanded_resource

    @staticmethod
    def compare_component(comp_1, comp_2):
        if comp_1 == '?' or comp_2 == '?':
            return True
        else:
            return comp_1 == comp_2

    def compare(self):
        return all(itertools.starmap(self.compare_component, zip(self.expanded_resource, self.expanded_string)))


def match_resource(resource, string):
    mr = _MatchResource(resource, string)
    return mr.compare()
