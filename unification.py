from unification.dispatch import dispatch
from unification.core import walk
from unification.ranged_variable import hasrange

from .variable import isvar

from .substitution import Substitution


@dispatch(object, object, Substitution)
def _unify(u, v, s):
    return False  # catch all

@dispatch(object, object, Substitution)
def unify(u, v, s):
    u = walk(u, s)
    v = walk(v, s)
    if u == v: # same symbol
        return s

    if isvar(u):
        if hasrange(u):
            if u.unify(v):
                return s.assoc(u, v)
            else:
                return False
        else:
            return s.assoc(u, v)
    if isvar(v):
        if hasrange(v):
            if v.unify(u):
                return s.assoc(u, v)
            else:
                return False
        else:
            return s.assoc(u, v)
    return _unify(u, v, s)

@dispatch(object, object)
def unify(u, v):
    return unify(u, v, Substitution())


