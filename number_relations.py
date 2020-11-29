
import numpy as np

from .substitution import Substitution
from .variable import TypedVar, isvar

def set_with_op(op):
    return

def gt(arg1, arg2):
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

def lt(arg1, arg2):
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
                rel_tensor = np.tri(arg1.type.size(), arg2.type.size(), 0, np.bool).T # places a1 > a2
                return sub.unify(rel_tensor, arg1, arg2)

        # if isvar(arg1):
        #     dim1 = sub.get_var_index(arg1)
        # if isvar(arg2):
        #     dim2 = sub.get_var_index(arg2)

    return goal


