"""
Diego Villalba 13-09-26

Forward checking: right after a variable is assigned, prune the domains of
the still-unassigned variables so any value that would already conflict
with the new assignment is removed. Lets backtrack detect a dead end
without having to recurse into it first.
"""

from src.csp.problem import CSP

# ____ Helper Functions ____


def forward_check(problem: CSP, assignment: dict, variable) -> dict | None:
    """Prune the domains of the unassigned variables after `variable` was set.

    Args:
        problem (CSP): CSP object, `problem.domains` is mutated in place
        assignment (dict): current assignment, already includes `variable`
        variable: the variable that was just assigned

    Returns:
        dict: mapping unassigned_variable -> tuple of the values removed
            from its domain, so the caller can undo the pruning later
        None: if some unassigned variable was left with an empty domain,
            meaning this branch cannot lead to a solution
    """

    removed = {}

    for other_var in problem.variables:
        if other_var in assignment or other_var == variable:
            continue
        kept_values = []
        removed_values = []

        for value in problem.domains[other_var]:
            # Here we explore the domain on each value ans asess
            # if its compatible keep it
            assignment[other_var] = value
            if problem.is_consistent(assignment):
                kept_values.append(value)
            else:
                removed_values.append(value)
            del assignment[other_var]

        if removed_values:
            # Keep track of removed values
            removed[other_var] = tuple(removed_values)

            # NOTE: Here we transform the global object in pytho
            # so we dont need to do it later
            problem.domains[other_var] = tuple(kept_values)
        if not kept_values:
            # Dead end: some variable has NO legal value left. Put back
            # whatever we already pruned in THIS call
            restore_domains(problem, removed)
            return None
    return removed


def restore_domains(problem: CSP, removed: dict) -> None:
    """Undo the pruning done by `forward_check`, putting the removed values back.

    Args:
        problem (CSP): CSP object, `problem.domains` is mutated in place
        removed (dict): mapping unassigned_variable -> tuple of removed
            values, exactly as returned by `forward_check`
    """
    for variable, values in removed.items():
        # append again removed variables
        problem.domains[variable] = problem.domains[variable] + values
