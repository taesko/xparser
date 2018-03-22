import collections


class Definitions(collections.UserDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.definitions = self.data

    def __getitem__(self, name):
        return self.definitions[name].value

    def __setitem__(self, key, value):
        if key in self:
            raise NotImplementedError()
        else:
            super().__setitem__(key, value)

    def __delitem__(self, key):
        raise NotImplementedError()