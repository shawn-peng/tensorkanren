import itertools as it
from functools import partial
from .util import (dicthash, interleave, take, multihash, unique, evalt)
from toolz import groupby, map

# from .unification import reify, unify, var  # noqa

#########
# Goals #
#########

# class Stream:
#     def __init__(self, iteratable):
#         self.iter = iter(iteratable)
#         self._move_next()
#
#     def __iter__(self):
#         return self
#
#     def __next__(self):
#         if self.first is not None:
#             ret = self.first
#             self._move_next()
#             return ret
#         else:
#             raise StopIteration
#
#     def _move_next(self):
#         try:
#             self.first = next(self.iter)
#         except StopIteration:
#             self.first = None
#
#     def empty(self):
#         return self.first is None
#
#
# def fail(s):
#     return Stream(())
#
#
# def success(s):
#     return Stream((s, ))


# def fail(s):
#     return iter(())
#
#
# def success(s):
#     return iter((s, ))


# def eq(u, v):
#     """ Goal such that u == v
#
#     See also:
#         unify
#     """
#
#     def goal_eq(s):
#         result = unify(u, v, s)
#         if result is not False:
#             yield result
#
#     return goal_eq
#
#
# ################################
# # Logical combination of goals #
# ################################
#
#
# def lall(*goals):
#     """ Logical all with goal reordering to avoid EarlyGoalErrors
#
#     See also:
#         EarlyGoalError
#         earlyorder
#
#     >>> from mykanren import lall, membero
#     >>> x = var('x')
#     >>> run(0, x, lall(membero(x, (1,2,3)), membero(x, (2,3,4))))
#     (2, 3)
#     """
#     return (lallgreedy, ) + tuple(earlyorder(*goals))
#
#
# def lallgreedy(*goals):
#     """ Logical all that greedily evaluates each goals in the order provided.
#
#     Note that this may raise EarlyGoalError when the ordering of the
#     goals is incorrect. It is faster than lall, but should be used
#     with care.
#
#     >>> from mykanren import eq, run, membero
#     >>> x, y = var('x'), var('y')
#     >>> run(0, x, lallgreedy((eq, y, set([1]))), (membero, x, y))
#     (1,)
#     >>> run(0, x, lallgreedy((membero, x, y), (eq, y, {1})))  # doctest: +SKIP
#     Traceback (most recent call last):
#       ...
#     kanren.core.EarlyGoalError
#     """
#     if not goals:
#         return success
#     if len(goals) == 1:
#         return goals[0]
#
#     def allgoal(s):
#         g = goaleval(reify(goals[0], s))
#         return unique(
#             interleave(goaleval(reify(
#                 (lallgreedy, ) + tuple(goals[1:]), ss))(ss) for ss in g(s)),
#             key=dicthash)
#
#     return allgoal
#
#
# def lallfirst(*goals):
#     """ Logical all - Run goals one at a time
#
#     >>> from mykanren import membero
#     >>> x = var('x')
#     >>> g = lallfirst(membero(x, (1,2,3)), membero(x, (2,3,4)))
#     >>> tuple(g({}))
#     ({~x: 2}, {~x: 3})
#     >>> tuple(lallfirst()({}))
#     ({},)
#     """
#     if not goals:
#         return success
#     if len(goals) == 1:
#         return goals[0]
#
#     def allgoal(s):
#         for i, g in enumerate(goals):
#             try:
#                 goal = goaleval(reify(g, s))
#             except EarlyGoalError:
#                 continue
#             other_goals = tuple(goals[:i] + goals[i + 1:])
#             return unique(
#                 interleave(
#                     goaleval(reify((lallfirst, ) + other_goals, ss))(ss)
#                     for ss in goal(s)),
#                 key=dicthash)
#         else:
#             raise EarlyGoalError()
#
#     return allgoal
#
#
# def lany(*goals):
#     """ Logical any
#
#     >>> from mykanren import lany, membero
#     >>> x = var('x')
#     >>> g = lany(membero(x, (1,2,3)), membero(x, (2,3,4)))
#     >>> tuple(g({}))
#     ({~x: 1}, {~x: 2}, {~x: 3}, {~x: 4})
#     """
#     if len(goals) == 1:
#         return goals[0]
#     return lanyseq(goals)
#
#
# def earlysafe(goal):
#     """ Call goal be evaluated without raising an EarlyGoalError """
#     try:
#         goaleval(goal)
#         return True
#     except EarlyGoalError:
#         return False
#
#
# def earlyorder(*goals):
#     """ Reorder goals to avoid EarlyGoalErrors
#
#     All goals are evaluated.  Those that raise EarlyGoalErrors are placed at
#     the end in a lall
#
#     See also:
#         EarlyGoalError
#     """
#     if not goals:
#         return ()
#     groups = groupby(earlysafe, goals)
#     good = groups.get(True, [])
#     bad = groups.get(False, [])
#
#     if not good:
#         raise EarlyGoalError()
#     elif not bad:
#         return tuple(good)
#     else:
#         return tuple(good) + ((lall, ) + tuple(bad), )
#
#
# def conde(*goalseqs):
#     """ Logical cond
#
#     Goal constructor to provides logical AND and OR
#
#     conde((A, B, C), (D, E)) means (A and B and C) or (D and E)
#     Equivalent to the (A, B, C); (D, E) syntax in Prolog.
#
#     See Also:
#         lall - logical all
#         lany - logical any
#     """
#     return (lany, ) + tuple((lall, ) + tuple(gs) for gs in goalseqs)
#
# def conda(*goalseqs):
#     # print(goalseqs)
#     # return success
#     def goal(s):
#         for gs in goalseqs:
#             if len(gs) == 1:
#                 print(gs)
#                 g = gs[0]
#                 evaled_g = goaleval(reify(g, s))
#                 print(evaled_g)
#                 new_s = Stream(evaled_g(s))
#                 if not new_s.empty():
#                     return new_s
#
#             g, rgs = gs
#             print(g, rgs)
#             print('reify', s, reify(g, s))
#             evaled_g = goaleval(reify(g, s))
#             print(evaled_g)
#             new_s = Stream(evaled_g(s))
#             # new_s = Stream(goaleval(reify(g, s))(s))
#             if new_s.empty():
#                 continue
#             return unique(interleave(
#                 goaleval(lall(rgs))(ss) for ss in new_s))
#             # for s in new_s:
#             #     print(s)
#             #     yield goaleval(lall(rgs))(s)
#             # break
#     return goal
#
#
# def lanyseq(goals):
#     """ Logical any with possibly infinite number of goals
#     """
#
#     def anygoal(s):
#         anygoal.goals, local_goals = it.tee(anygoal.goals)
#
#         def f(goals):
#             for goal in goals:
#                 try:
#                     yield goaleval(reify(goal, s))(s)
#                 except EarlyGoalError:
#                     pass
#
#         return unique(
#             interleave(
#                 f(local_goals),
#                 pass_exceptions=[EarlyGoalError]),
#             key=dicthash)
#
#     anygoal.goals = goals
#
#     return anygoal
#
#
# def condeseq(goalseqs):
#     """
#     Like conde but supports generic (possibly infinite) iterator of goals
#     """
#     return (lanyseq, ((lall, ) + tuple(gs) for gs in goalseqs))
#
#
# def everyg(predicate, coll):
#     """
#     Asserts that predicate applies to all elements of coll.
#     """
#     return (lall, ) + tuple((predicate, x) for x in coll)


########################
# User level execution #
########################


def run(n, x, *goals):
    """ Run a logic program.  Obtain n solutions to satisfy goals.

    n     - number of desired solutions.  See ``take``
            0 for all
            None for a lazy sequence
    x     - Output variable
    goals - a sequence of goals.  All must be true

    >>> from mykanren import run, var, eq
    >>> x = var()
    >>> run(1, x, eq(x, 1))
    (1,)
    """
    # results = map(partial(reify, x), goaleval(lall(*goals))({}))
    # return take(n, unique(results, key=multihash))
    pass



# ###################
# # Goal Evaluation #
# ###################
#
#
# class EarlyGoalError(Exception):
#     """ A Goal has been constructed prematurely
#
#     Consider the following case
#
#     >>> from mykanren import run, eq, membero, var
#     >>> x, coll = var(), var()
#     >>> run(0, x, (membero, x, coll), (eq, coll, (1, 2, 3))) # doctest: +SKIP
#
#     The first goal, membero, iterates over an infinite sequence of all possible
#     collections.  This is unproductive.  Rather than proceed, membero raises an
#     EarlyGoalError, stating that this goal has been called early.
#
#     The goal constructor lall Logical-All-Early will reorder such goals to
#     the end so that the call becomes
#
#     >>> run(0, x, (eq, coll, (1, 2, 3)), (membero, x, coll)) # doctest: +SKIP
#
#     In this case coll is first unified to ``(1, 2, 3)`` then x iterates over
#     all elements of coll, 1, then 2, then 3.
#
#     See Also:
#         lall
#         earlyorder
#     """
#
#
# def find_fixed_point(f, arg):
#     """
#     Repeatedly calls f until a fixed point is reached.
#
#     This may not terminate, but should if you apply some eventually-idempotent
#     simplification operation like evalt.
#     """
#     last, cur = object(), arg
#     while last != cur:
#         last = cur
#         cur = f(cur)
#     return cur
#
#
# def goaleval(goal):
#     """ Expand and then evaluate a goal
#
#     Idempotent
#
#     See also:
#        goalexpand
#     """
#     if callable(goal):  # goal is already a function like eq(x, 1)
#         return goal
#     if isinstance(goal, tuple):  # goal is not yet evaluated like (eq, x, 1)
#         try:
#             return find_fixed_point(evalt, goal)
#         except Exception as e:
#             raise EarlyGoalError(e)
#     raise TypeError("Expected either function or tuple")
