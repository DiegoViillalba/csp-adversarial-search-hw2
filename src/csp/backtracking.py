"""
Diego Villalba 12-09-26

General backtracking search for finite CSPs.
"""

from collections.abc import Callable

from src.csp.forward_checking import forward_check, restore_domains
from src.csp.problem import CSP

# ____ Helper Functions ____


def select_unassigned_variable(problem: CSP, assignment: dict):
    """
    Return the next abviable variable to assign
    """
    for variable in problem.variables:
        if variable not in assignment:
            return variable

    return None


def backtrack(
    problem: CSP,
    assignment: dict,
    heuristic: Callable | None = None,
    value_order: Callable | None = None,
    forward_checking: bool = False,
) -> dict | None:

    """Return a complete consistent assignment, or ``None`` if none exists."""

    if not problem.is_consistent(assignment):
        return None

    if all(variable in assignment for variable in problem.variables):
        return assignment.copy()

    if heuristic:
        variable = heuristic(problem,assignment)
    else:
        variable = select_unassigned_variable(problem, assignment)

    values = problem.domains[variable]

    if value_order:
        values = value_order(problem, assignment, variable)

    for value in values:
        assignment[variable] = value

        removed = None
        if forward_checking:
            removed = forward_check(problem, assignment, variable)
            if removed is None:
                del assignment[variable]
                continue

        result = backtrack(problem, assignment, heuristic, value_order, forward_checking)
        if result is not None:
            return result

        if forward_checking:
            restore_domains(problem, removed)

        del assignment[variable]

    return None
