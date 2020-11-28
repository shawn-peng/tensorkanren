
_var_types = {}

class VarType:
    def __init__(self, typename, valtype):
        if typename in _var_types:
            raise KeyError('duplicated type name', typename)
        self.name = typename
        self.valtype = valtype
        self.valmap = {}
        self.indmap = {}
        self.n = 0

        _var_types[typename] = self

    @staticmethod
    def get_type(typename):
        if typename not in _var_types:
            raise KeyError('type not found', typename)
        return _var_types[typename]

    def encode(self, k):
        return self.indmap[k]

    def decode(self, k):
        return self.valmap[k]

    def add_value(self, v):
        if v not in self.indmap:
            self.indmap[v] = self.n
            self.valmap[self.n] = v
            self.n += 1

    def get_values(self):
        return self.indmap.keys()

    def size(self):
        return self.n