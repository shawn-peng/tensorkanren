from unification import unify, reify

from .util import intersection
from toolz import merge

from collections import defaultdict

# class _recursive_enumerate(object):
# def _recursive_enumerate(iter, ):
#     i = 0
#     for it in iter:
#         if isinstance(it, tuple):



class Relation(object):
    _id = 0

    def __init__(self, name=None):
        self.facts = set()
        self.index = dict()
        if not name:
            name = "_%d" % Relation._id
            Relation._id += 1
        self.name = name
        self.value_collections = []

    def add_fact(self, *inputs):
        """ Add a fact to the knowledgebase.

        See Also:
            fact
            facts
        """
        fact = tuple(inputs)

        self.facts.add(fact)

        for key in enumerate(inputs):
            if len(self.value_collections) <= key[0]:
                self.value_collections.append(set())
            self.value_collections[key[0]].add(key[1])
            if key not in self.index:
                self.index[key] = set()
            self.index[key].add(fact)

    def get_values(self, argpos):
        if argpos >= len(self.value_collections):
            return []
        return self.value_collections[argpos]

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

        def goal(substitution):
            args2 = reify(args, substitution)
            subsets = [self.index[key] for key in enumerate(args)
                       if key in self.index]
            if subsets:  # we are able to reduce the pool early
                facts = intersection(*sorted(subsets, key=len))
            else:
                facts = self.facts

            for fact in facts:
                unified = unify(fact, args2, substitution)
                if unified != False:
                    yield merge(unified, substitution)

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
