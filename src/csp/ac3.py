"""
Diego Villalba 14-09-26

AC3: enforce arc consistency on a CSP before search even starts. For every
ordered pair of variables (Xi, Xj), every value left in Xi's domain must
have at least one compatible value in Xj's domain, or it gets removed.
Removing a value can break consistency for pairs that were already fine,
so those go back on the queue to be re-checked.

NOTE: since the implementation of this algorithm we added a adjacency dict
so we keep track of the neightbor values to avoidexporing all of them
"""

from collections import deque

from src.csp.problem import CSP

# ____ Helper Functions ____


def revise(problem: CSP, xi, xj) -> bool:
    """Remove values from Xi's domain that have no supporting value in Xj's domain.

    Args:
        problem (CSP): CSP object, `problem.domains` is mutated in place
        xi: the variable whose domain may get pruned
        xj: the variable being checked against

    Returns:
        bool: True if Xi's domain was actually reduced
    """
    kept_values = []

    for x in problem.domains[xi]:
        # "Support" = at least one y in Xj's domain such that (xi=x, xj=y)
        # doesn't violate a constraint. We build a 2-entry dict {xi: x, xj: y}
        has_support = any(
            problem.is_consistent({xi: x, xj: y}) for y in problem.domains[xj]
        )
        if has_support:
            kept_values.append(x)

    revised = len(kept_values) < len(problem.domains[xi])
    if revised:
        problem.domains[xi] = tuple(kept_values)

    return revised


def ac3(problem: CSP) -> bool:
    """Enforce arc consistency on every variable's domain.

    Args:
        problem (CSP): CSP object, `problem.domains` is mutated in place

    Returns:
        bool: False if some domain was emptied out (the CSP has no
            solution), True otherwise (arc-consistent, but not
            necessarily solvable — that's still backtrack's job)
    """
    # Start with every ordered pair (Xi, Xj), Xi != Xj, as a candidate arc.
    # Order matters: (Xi, Xj) and (Xj, Xi) are two different checks —
    # revising Xi against Xj doesn't automatically revise Xj against Xi.

    # NOTE: Implementation of an optimization with neighbors in case of adj dict

    if problem.neighbors:
        queue = deque(
            (xi, xj) for xi in problem.variables for xj in problem.neighbors[xi]
        )
    else:
        queue = deque(
            (xi, xj) for xi in problem.variables for xj in problem.variables if xi != xj
        )

    while queue:
        xi, xj = queue.popleft()

        if revise(problem, xi, xj):
            # Xi's domain just shrank. If it's now empty, no value of Xi
            # can ever work -> the whole CSP is unsatisfiable, stop here.
            if not problem.domains[xi]:
                return False

            # Any OTHER variable Xk that constrains Xi might have relied on
            # a value we just removed from Xi -> its own arc (Xk, Xi) needs
            # to be re-checked. When we know the real constraint graph, only
            # Xi's actual neighbors can be affected -- everyone else was
            # never constrained against Xi in the first place.
            if problem.neighbors is not None:
                requeue = (xk for xk in problem.neighbors[xi] if xk != xj)
            else:
                requeue = (xk for xk in problem.variables if xk != xi and xk != xj)
            for xk in requeue:
                queue.append((xk, xi))

    return True
