
import numpy as np

from .facts import Relation
from .substitution import Substitution
from .variable import TypedVar, isvar
from .types import VarType

def set_with_op(op):
    return

class NumberRelation(Relation):
    '''
    direction: +1 -1 = sign(a2 - a1)
    include: 0 1
    '''
    def __init__(self, arg_types, direction, include):
        name = ['g', 't']
        if direction > 0:
            name[0] = 'l'
        if include:
            name[1] = 'e'
        name = "".join(name)
        super().__init__(arg_types, name)
        self.d = direction
        self.i = include

    def __call__(self, arg1, arg2):
        def goal(sub: Substitution):
            # def get_rel_tensor():
            if not isvar(arg1):
                if not isvar(arg2):  # const, const
                    rel_tensor = np.array(False, np.bool)
                    return sub.unify(rel_tensor)
                else:  # const, var
                    rel_tensor = arg2.type.zeros()
                    ind = arg2.type.encode(arg1)
                    rel_tensor[ind::self.d] = 1 # set True along arg1 -> arg2
                    rel_tensor[ind] = self.i # set as include, avoiding if branch
                    return sub.unify(rel_tensor, arg2)
            else:
                if not isvar(arg2):  # var, const
                    rel_tensor = arg1.type.zeros()
                    ind = arg1.type.encode(arg2)
                    rel_tensor[ind::-self.d] = 1 # set True along arg1 <- arg2, inverted direction with -d
                    rel_tensor[ind] = self.i # set as include, avoiding if branch
                    return sub.unify(rel_tensor, arg1)
                else:  # var, var
                    assert (arg1.type == arg2.type)
                    # if include, set True on diag, so pass 0, otherwise pass 1
                    # lower triangle set True, places a1 > a2
                    rel_tensor = np.tri(arg1.type.size(), arg2.type.size(), 1-self.i, np.bool)  # places a1 > a2
                    # for - direction, a1 < a2, take transpose
                    rel_tensor = rel_tensor.T
                    return sub.unify(rel_tensor, arg1, arg2)

            # if isvar(arg1):
            #     dim1 = sub.get_var_index(arg1)
            # if isvar(arg2):
            #     dim2 = sub.get_var_index(arg2)

        return goal

VarType('ordinal', 'oridinal')
numtype = VarType.get_type('ordinal')
arg_types = (numtype, numtype)
gt = NumberRelation(arg_types, -1, 0)
ge = NumberRelation(arg_types, -1, 1)
lt = NumberRelation(arg_types, 1, 0)
le = NumberRelation(arg_types, 1, 1)

def _gt(arg1, arg2):
    def goal(sub: Substitution):
        # def get_rel_tensor():
        if not isvar(arg1):
            if not isvar(arg2): # const, const
                rel_tensor = np.array(False, np.bool)
                return sub.unify(rel_tensor)
            else: # const, var
                rel_tensor = arg2.type.ones()
                ind = arg2.type.encode(arg1)
                rel_tensor[ind:] = 0
                return sub.unify(rel_tensor, arg2)
        else:
            if not isvar(arg2): # var, const
                rel_tensor = arg1.type.ones()
                ind = arg1.type.encode(arg2)
                rel_tensor[ind:] = 0
                return sub.unify(rel_tensor, arg1)
            else: # var, var
                assert(arg1.type == arg2.type)
                rel_tensor = np.tri(arg1.type.size(), arg2.type.size(), 1, np.bool) # places a1 > a2
                return sub.unify(rel_tensor, arg1, arg2)

        # if isvar(arg1):
        #     dim1 = sub.get_var_index(arg1)
        # if isvar(arg2):
        #     dim2 = sub.get_var_index(arg2)

    return goal

def _lt(arg1, arg2):
    def goal(sub: Substitution):
        # def get_rel_tensor():
        if not isvar(arg1):
            if not isvar(arg2): # const, const
                rel_tensor = np.array(False, np.bool)
                return sub.unify(rel_tensor)
            else: # const, var
                rel_tensor = arg2.type.ones()
                ind = arg2.type.encode(arg1)
                rel_tensor[ind::-1] = 0
                return sub.unify(rel_tensor, arg2)
        else:
            if not isvar(arg2): # var, const
                rel_tensor = arg1.type.ones()
                ind = arg1.type.encode(arg2)
                rel_tensor[ind::-1] = 0
                return sub.unify(rel_tensor, arg1)
            else: # var, var
                assert(arg1.type == arg2.type)
                rel_tensor = np.tri(arg1.type.size(), arg2.type.size(), 0, np.bool).T # places a1 < a2
                return sub.unify(rel_tensor, arg1, arg2)

        # if isvar(arg1):
        #     dim1 = sub.get_var_index(arg1)
        # if isvar(arg2):
        #     dim2 = sub.get_var_index(arg2)

    return goal


