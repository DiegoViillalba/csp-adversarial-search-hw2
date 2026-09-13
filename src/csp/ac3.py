"""
Diego Villalba 12-09-26

AC3: enforce arc consistency on a CSP before search even starts. For every
ordered pair of variables (Xi, Xj), every value left in Xi's domain must
have at least one compatible value in Xj's domain, or it gets removed.
Removing a value can break consistency for pairs that were already fine,
so those go back on the queue to be re-checked.

NOTE: since CSP does not expose an explicit neighbor/constraint graph, this
treats every pair of variables as a potential arc and lets `is_consistent`
decide whether they actually constrain each other. Correct for all three
of our problems, but on a large sparse graph (the 1000-node coloring
instance) it re-checks many pairs that were never actually connected —
an explicit neighbors structure on CSP would let us only queue real arcs.
Left as-is for now given the time we have.
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
    queue = deque(
        (xi, xj)
        for xi in problem.variables
        for xj in problem.variables
        if xi != xj
    )

    while queue:
        xi, xj = queue.popleft()

        if revise(problem, xi, xj):
            if not problem.domains[xi]:
                return False

            for xk in problem.variables:
                if xk != xi and xk != xj:
                    queue.append((xk, xi))

    return True
