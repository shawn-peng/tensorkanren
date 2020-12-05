from unification import unify, reify
from unification.variable import isvar
from .substitution import Substitution
# import numpy as np

from .util import intersection
from toolz import merge

from collections import defaultdict
import torch
# class _recursive_enumerate(object):
# def _recursive_enumerate(iter, ):
#     i = 0
#     for it in iter:
#         if isinstance(it, tuple):


relation_facts_tensor = torch.sparse #torch.ndarray

class Relation(object):
    _id = 0

    def __init__(self, arg_types, name=None):
        self.facts = set()
        self.index = dict()
        if not name:
            name = "_%d" % Relation._id
            Relation._id += 1
        self.name = name
        self.arg_types = arg_types
        # self.value_collections = []
        # self.arg_types = arg_types
        self.facts_tensor = None

    def add_fact(self, *inputs):
        """ Add a fact to the knowledgebase.

        See Also:
            fact
            facts
        """
        fact = tuple(inputs)

        self.facts.add(fact)

        for key in enumerate(inputs):
            # if len(self.value_collections) <= key[0]:
            #     self.value_collections.append(set())
            # self.value_collections[key[0]].add(key[1])
            self.arg_types[key[0]].add_value(key[1])
            if key not in self.index:
                self.index[key] = set()
            self.index[key].add(fact)

    def encode_fact(self, *args):
        ind = tuple([ self.arg_types[i].encode(k) for i, k in enumerate(args) ])
        return ind

    def decode_fact(self, *ind):
        return tuple([ self.arg_types[i].decode(k) for i, k in enumerate(ind) ])

    def compile_facts(self):
        self.key_indices = []
        shape = []
        for type in self.arg_types:
            shape.append(type.size())
        # for i, keys in enumerate(self.value_collections):
        #     shape.append(len(keys))
        #     key_map = {k: j for j, k in enumerate(keys)}
        #     self.key_indices.append(key_map)

        print(self.facts)
        # self.facts_tensor = torch.array(list(self.facts))
        self.facts_tensor = torch.zeros(shape, dtype=torch.bool)
        for fact in self.facts:
            ind = self.encode_fact(*fact)
            self.facts_tensor[ind] = True

    def get_values(self, argpos):
        # if argpos >= len(self.value_collections):
        #     return []
        # return self.value_collections[argpos]
        return self.arg_types[argpos].get_values()

    def __call__(self, *args):
        """ Returns an evaluated (callable) goal, which returns a list of
        substitutions which match args against a fact in the knowledge base.

        *args: the goal to evaluate. This consists of vars and values to
               match facts against.

        >>> from mykanren.facts import Relation
        >>> from unification import var
        >>>
        >>> x, y = var('x'), var('y')
        >>> r = Relation()
        >>> r.add_fact(1, 2, 3)
        >>> r.add_fact(4, 5, 6)
        >>> list(r(x, y, 3)({})) == [{y: 2, x: 1}]
        True
        >>> list(r(x, 5, y)({})) == [{y: 6, x: 4}]
        True
        >>> list(r(x, 42, y)({}))
        []
        """

        def goal(sub):
            # if isinstance(sub, dict)
            if not isinstance(sub, Substitution):
                if isinstance(sub, dict):
                    sub = Substitution(sub)
                else:
                    raise TypeError('in tensorKanren a the substitution for a goal should be a instance of class Substitution')
            # args2 = reify(args, sub) # consider to change to sub.reify_last_var

            # result = self.facts_tensor
            # for i, arg in enumerate(reversed(args2)):
            #     if isinstance(arg, relation_facts_tensor):
            #         if arg.ndim == 1:
            #             shape = [len(arg)] + [1]*i
            #             arg.reshape(shape)
            #             result = result * arg.reshape(shape)
            #         else:
            #             raise TypeError('multi-dimensional variable not supported yet')
            # inds = map(sub.get_var_index, args)

            # for arg in args:
            #     ind = sub.get_var_index(arg)

            # unified = {}
            # inner_res = result

            if self.facts_tensor is None:
                self.compile_facts()

            nonlocal args
            nargs = len(args)
            varargs = []
            ind = [slice(None)] * nargs
            for i, arg in enumerate(args):
                if isvar(arg):
                    varargs.append(arg)
                else:
                    ind[i] = self.arg_types[i].encode(arg)
            ind = tuple(ind)

            newsub = sub.unify(self.facts_tensor[ind], *varargs)
            # for arg in reversed(args2):
            #     if isvar(arg):
            #         #m = sub.reify_last_var(arg)
            #         unified[arg] = inner_res
            #         newsub[arg] = inner_res
            #     inner_res = inner_res.sum(axis=-1) != 0

            return newsub




            # sub.assoc()
            # subsets = [self.index[key] for key in enumerate(args)
            #            if key in self.index]
            # if subsets:  # we are able to reduce the pool early
            #     facts = intersection(*sorted(subsets, key=len))
            # else:
            #     facts = self.facts
            #
            # for fact in facts:
            #     unified = unify(fact, args2, substitution)
            #     if unified != False:
            #         yield merge(unified, substitution)

        return goal

    def __str__(self):
        return "<Rel: " + self.name + ">"

    __repr__ = __str__


def fact(rel, *args):
    """ Declare a fact

    >>> from mykanren import fact, Relation, var, run
    >>> parent = Relation()
    >>> fact(parent, "Homer", "Bart")
    >>> fact(parent, "Homer", "Lisa")

    >>> x = var()
    >>> run(1, x, parent(x, "Bart"))
    ('Homer',)
    """
    rel.add_fact(*args)


def facts(rel, *lists):
    """ Declare several facts

    >>> from mykanren import fact, Relation, var, run
    >>> parent = Relation()
    >>> facts(parent,  ("Homer", "Bart"),
    ...                ("Homer", "Lisa"))

    >>> x = var()
    >>> run(1, x, parent(x, "Bart"))
    ('Homer',)
    """
    for l in lists:
        fact(rel, *l)
