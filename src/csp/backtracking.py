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
    find_all: bool = False,
    solutions_accumulator: list[dict] | None = None,  # NEW: Pass a mutable list to save progress safely
) -> dict | list[dict] | None:
    """Return a complete consistent assignment, or a list of all solutions if find_all is True,

    or ``None`` if none exists.

    node_counter, if given, is a one-element list incremented once per
    call -- i.e. once per node/state visited in the search tree. A list
    (not an int) because ints are immutable in Python: passing one down
    the recursion wouldn't let child calls update the caller's copy. None
    (the default) skips counting entirely, so callers that don't care
    about this pay no extra cost.
    """

    # NEW: Initialize the accumulator if we are finding all solutions and none was provided
    if find_all and solutions_accumulator is None:
        solutions_accumulator = []

    # NOTE: Internal recursive worker
    def _search(curr_assignment: dict) -> dict | None:
        if node_counter is not None:
            node_counter[0] += 1

        if not problem.is_consistent(curr_assignment):
            return None

        # Every variable has a value -> we're done, this branch is a solution.
        # NOTE: .copy() matters here: `assignment` keeps getting mutated
        if all(variable in curr_assignment for variable in problem.variables):
            if find_all:
                # NEW: Append directly to the referenced list and return None to force backtracking (keep exploring)
                solutions_accumulator.append(curr_assignment.copy())
                return None
            return curr_assignment.copy()

        # Current Heuristic-selection, we fall back to the naive "first unassigned" order.
        if heuristic:
            variable = heuristic(problem, curr_assignment)
        else:
            variable = select_unassigned_variable(problem, curr_assignment)

        values = problem.domains[variable]

        if value_order:
            values = value_order(problem, curr_assignment, variable)

        for value in values:
            # Tentative assignment
            curr_assignment[variable] = value

            removed = {}
            if forward_checking:
                # Prune the OTHER unassigned variables' domains right now,
                # NOTE: This call mutes the domains inside the function
                # so we dont need to do anything more
                removed = forward_check(problem, curr_assignment, variable)
                if removed is None:
                    del curr_assignment[variable]
                    continue

            result = _search(curr_assignment)

            # NEW: If we are NOT in find_all mode, and we found a result, propagate it up
            if not find_all and result is not None:
                if forward_checking:
                    restore_domains(problem, removed)
                del curr_assignment[variable]
                return result

            # NOTE: If this result returned none, reconstruct the pruned domains
            # before continuing backtracking
            if forward_checking:
                restore_domains(problem, removed)

            del curr_assignment[variable]

        return None

    # Start the search
    single_result = _search(assignment)

    # NEW: Return the accumulator list if find_all is True, else return the single result
    if find_all:
        return solutions_accumulator
    return single_result