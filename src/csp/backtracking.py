"""
Diego Villalba 12-09-26

General backtracking search for finite CSPs.
"""

from collections.abc import Callable

from src.csp.forward_checking import forward_check, restore_domains
from src.csp.problem import CSP

# ____ Helper Functions ____


def select_unassigned_variable(problem: CSP, assignment: dict):
    """Default non hauristic ordering

    Args:
        problem (CSP): CSP object containning all its variables
        assignment (dict): current assignment dictionary
        This is the function `heuristic=mrv` (or any other) replaces.

    Returns:
        _type_: choosen variable or None
    """
    for variable in problem.variables:
        if variable not in assignment:
            return variable

    return None


# ______ Main backtracking implementation ______


def backtrack(
    problem: CSP,
    assignment: dict,
    heuristic: Callable | None = None,
    value_order: Callable | None = None,
    forward_checking: bool = False,
    node_counter: list[int] | None = None,
) -> dict | None:
    """Return a complete consistent assignment, or ``None`` if none exists.

    node_counter, if given, is a one-element list incremented once per
    call -- i.e. once per node/state visited in the search tree. A list
    (not an int) because ints are immutable in Python: passing one down
    the recursion wouldn't let child calls update the caller's copy. None
    (the default) skips counting entirely, so callers that don't care
    about this pay no extra cost.
    """

    if node_counter is not None:
        node_counter[0] += 1

    if not problem.is_consistent(assignment):
        return None

    # Every variable has a value -> we're done, this branch is a solution.
    # NOTE: .copy() matters here: `assignment` keeps getting mutated
    if all(variable in assignment for variable in problem.variables):
        return assignment.copy()

    # Current Heuristic-selection, we fall back to the naive "first unassigned" order.
    if heuristic:
        variable = heuristic(problem, assignment)
    else:
        variable = select_unassigned_variable(problem, assignment)

    values = problem.domains[variable]

    if value_order:
        values = value_order(problem, assignment, variable)

    for value in values:
        # Tentative assignment
        assignment[variable] = value

        removed = {}
        if forward_checking:
            # Prune the OTHER unassigned variables' domains right now,
            # NOTE: This call mutes the domains inside the function
            # so we dont need to do anything more
            removed = forward_check(problem, assignment, variable)
            if removed is None:
                del assignment[variable]
                continue

        result = backtrack(
            problem, assignment, heuristic, value_order, forward_checking, node_counter
        )
        if result is not None:
            return result

        # NOTE: If this result returned none, reconstruct the pruned domains
        # before continuing backtracking
        if forward_checking:
            restore_domains(problem, removed)

        del assignment[variable]

    return None
