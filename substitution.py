from .variable import isvar
from temp_dict import temp_dict

from collections import defaultdict
from itertools import starmap
# import numpy as np
import torch
from .variable import Var, TypedVar, VarType

class typedValue:
    def __init__(self, type: str, val):
        self.type = type
        self.val = val

# class substitution(dict):
class Substitution(temp_dict):
    def __init__(self, d: dict):
        super(Substitution, self).__init__(d)
        # self.result = torch.array([1], dtype=torch.bool)
        self.result = torch.ones([1],dtype = torch.bool)
        # print(self.result)
        self.var_indices = defaultdict(lambda: len(self.var_indices))
        if isinstance(d, Substitution):
            self.result = d.result
            self.var_indices.update(d.var_indices)
        # else:
        #     raise TypeError('invalid arg type', type(d))

    def _reify_last_var(self, u):
        if u in self:
            v = self[u]
            if isvar(v):
                return self._reify_last_var(v)
        # either u is not associated or is associated with a value
        return u

    # walk through the substitution but stay at the last variable, so that we know whom we should change the map
    def reify_last_var(self, u):
        if not isvar(u):
            raise TypeError('reify_last_var only accept variable inputs')
        return self._reify_last_var(u)

    def set_result(self, res):
        self.result = res

    # def add_var(self, u):
    #     if u not in self.var_indices:
    #         new_ind = len(self.var_indices)
    #         self.var_indices[u] = new_ind

    def get_var_index(self, u):
        if isvar(u):
            return self.var_indices[u]
        ## disable direct indexing for now
        # elif isinstance(u, int):
        #     return u
        else:
            raise TypeError('Invalide type for var', u)

    def get_var_indices(self, vars):
        return tuple(map(self.get_var_index, vars))

    def get_var_values(self, *args):
        ind = [self.get_var_index(arg) for arg in args]
        sumdims = tuple([i for i in range(len(self.result.shape)) if i not in ind])
        if sumdims:
            val = self.result.any(sumdims)
        else: # all dims in args
            # print(ind)
            val = self.result.transpose(ind[0],ind[0]-1) # may need transpose
        return val

    def reify(self, *args):
        # ind = self.get_var_index(u)
        res = self.reduce_to(*args)
        for ind in torch.argwhere(res):
            yield tuple((starmap(lambda arg, v: arg.type.decode(v), zip(args, ind))))

    # def decode(self):

    def unify(self, rel_tensor, *args):
        # n dims of rel_tensor should match number of args
        # args is used only to indicate dimensions
        rel_tensor = rel_tensor
        newsub = Substitution(self)
        if args is None: # constant relation
            newsub.result = newsub.result * rel_tensor # make a copy
            return newsub
        # dims = [newsub.var_indices[arg] for arg in args] # get dims for vars adding new dim if needed
        dims = list(newsub.get_var_indices(args))
        # newsub.var_indices
        dims_sort_ind = torch.argsort(torch.FloatTensor(dims))
        s0 = rel_tensor.shape
        ndim1 = len(newsub.var_indices)
        # s1 = [1]*ndim1
        # s1 = range(ndim1)

        ndim0 = len(newsub.result.shape)
        newdim = ndim0
        if ndim0 < ndim1:
            newdim = ndim1
            newsub.result = torch.expand_dims(newsub.result, list(range(ndim0, ndim1)))

        # s1 = []
        # for i in range(newdim):
        #     if i not in dims:
        #         s1.append(i)
        s1flags = torch.ones(newdim, dtype=torch.bool)
        s1flags[dims] = 0
        #newdims = torch.arange(ndim1)
        exp_dims = torch.arange(newdim)
        exp_dims = list(exp_dims[s1flags])
        rel_tensor = rel_tensor.transpose(dims_sort_ind[0],dims_sort_ind[0]-1) #order
        if exp_dims:
            rel_tensor = torch.expand_dims(rel_tensor, exp_dims) #align

        newsub.result = newsub.result * rel_tensor # broadcasting other dimensions

        return newsub # return new substituion

    def __len__(self):
        return len(self.var_indices)

    def _sub_or(self, other):
        n1 = len(self)
        n2 = len(other)

        newsub = Substitution(self)

        r1 = self.result
        r2 = other.result
        if n1 > n2:
            newsub.var_indices.update(self.var_indices)
            r2 = torch.expand_dims(r2, range(n2, n1))
        elif n1 < n2:
            newsub.var_indices.update(other.var_indices)
            r1 = torch.expand_dims(r1, range(n1, n2))

        newsub.result = r1 | r2
        return newsub

    def __or__(self, other):
        if isinstance(other, Substitution):
            return self._sub_or(other)


    def __and__(self, other):
        n1 = len(self)
        n2 = len(other)

        r1 = self.result
        r2 = other.result
        if n1 > n2:
            r2 = torch.expand_dims(r2, range(n2, n1))
        elif n1 < n2:
            r1 = torch.expand_dims(r1, range(n1, n2))

        return r1 & r2

    def __repr__(self):
        # return "<Substituion>:\n\t<vars>: %s,\n\t<result tensor>: %s" % (str(self.var_indices), str(self.result))
        return "<Substituion>:\n\t<vars>: %s,\n\t<non-zeros>: %s" % (str(self.var_indices), str(self.result.sum()))

    def reduce(self, *args, op=torch.any):
        dims = self.get_var_indices(args)
        dims_sort_ind = torch.argsort(dims)
        dims_trans = torch.zeros(len(dims_sort_ind), int)
        dims_trans[dims_sort_ind] = torch.arange(len(dims_sort_ind))
        return op(self.result, dims).transpose(dims_trans)

    def reduce_to(self, *args, op=torch.any):
        if not args:
            return op(self.result)
        dims = self.get_var_indices(args)
        r_dim = torch.FloatTensor(tuple([i for i in range(len(self)) if i not in dims]))
        dims_sort_ind = torch.argsort( torch.FloatTensor(dims))
        # print(dims_sort_ind)
        dims_trans = torch.zeros(len(dims_sort_ind), dtype = int)
        dims_trans[dims_sort_ind] = torch.arange(len(dims_sort_ind))
        return op(self.result, r_dim).transpose(dims_trans)

    def filter(self, args, data):
        newsub = Substitution(self)

        ind = self.get_var_indices(args)

        exp_ind = list(range(len(self)))
        for i in ind:
            exp_ind.remove(i)
        data = torch.expand_dims(data, exp_ind)

        newsub.result = self.result * data
        return newsub

    def count(self, *args):
        return self.reduce_to(*args).sum()

    # def


    # def _walk(self, x):
    #     while x in self:
    #         x = self[x]
    #     return x

    # def __getitem__(self, item):
