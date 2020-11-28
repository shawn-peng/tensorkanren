
from functools import partial
from unification.dispatch import dispatch
from unification.ranged_variable import hasrange
from unification.utils import hashable

from .types import VarType

_global_logic_variables = set()
_glv = _global_logic_variables

# def var(type: str):
#     return

# def getVarType(type: str):
#     return _VarTypeDict[type]

# class VarType:
#
#     def __init__(self, name: str):
#         self.name = name
#         self.var_dict = {}
#
#     def Var(self, name: str):
#         var = Var(self, name)
#         self.var_dict[name] = var
#         return var

    # def newVar(self):

class Var:
    def __init__(self, name: str):
        self.name = name

    def unify(self, other):
        if hasrange(self):
            pass


@dispatch(Var)
def isvar(v):
    return True


@dispatch(object)
def isvar(o):
    return not not _glv and hashable(o) and o in _glv


class TypedVar(Var):
    def __init__(self, type: VarType, name: str):
        super().__init__(name)
        self.type = type




_VarTypeDict = {}
