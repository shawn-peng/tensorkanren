
import numpy as np

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
        
        self.values = set()
        self.compiled = False

        _var_types[typename] = self

    @staticmethod
    def get_type(typename):
        if typename not in _var_types:
            raise KeyError('type not found', typename)
        return _var_types[typename]

    def fit(self, a):
        if self.valtype == 'oridinal':
            a = sorted(a)
        for v in a:
            self.add_value(v)
        self.compile_index()
    
    def compile_index(self):
        self.n = len(self.values)
        for i, v in enumerate(self.values):
            self.indmap[v] = i
            self.valmap[i] = v
        self.compiled = True

    def encode(self, k):
        if not self.compiled:
            self.compile_index()
        return self.indmap[k]

    def decode(self, k):
        if not self.compiled:
            self.compile_index()
        return self.valmap[k]

    def add_value(self, v):
        # if v not in self.indmap:
        #     self.indmap[v] = self.n
        #     self.valmap[self.n] = v
        #     self.n += 1
        self.values.add(v)

    def get_values(self):
        # return self.indmap.keys()
        return self.values

    def size(self):
        if not self.compiled:
            self.compile_index()
        return self.n

    def zeros(self):
        if not self.compiled:
            self.compile_index()
        return np.zeros(self.n, np.bool)

    def ones(self):
        if not self.compiled:
            self.compile_index()
        return np.ones(self.n, np.bool)

    def __repr__(self):
        return "<%s>%s" % (self.valtype, self.name)
