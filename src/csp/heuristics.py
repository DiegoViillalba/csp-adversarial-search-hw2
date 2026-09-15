"""
Diego Villalba 12-09-26
Clasical heuristics implementation in backtracking search
"""

from src.csp.problem import CSP


def mrv(problem: CSP, assignment: dict):
    """Minnimum remaining value implementation

    Main idea, instead of blindly chooing the first non
    used variable, well use the one that has least legal
    values on its domain. By that the algorithm ends up
    failing faster on deemed branches

    Args:
        problem (CSP): CSP object
        assignment (dict): current asignment

    Returns:
        _type_: best variable to follow
    """
    non_assigned = [v for v in problem.variables if v not in assignment]

    best_variable = None

    # Biggest than anything
    least_count = float("inf")

    for var in non_assigned:
        count = 0
        for value in problem.domains[var]:
            assignment[var] = value
            if problem.is_consistent(assignment):
                count += 1
            del assignment[var]

        if count < least_count:
            least_count = count
            best_variable = var

    return best_variable


def lcv(problem: CSP, assignment: dict, variable):
    """Least constraining value implementation
    Main idea, once weve choosen the variable we shall try first
    the value that "steals" least options from the remainning
    unassigned variables

    Args:
        problem (CSP): CSP object
        assignment (dict): current assignment of variable:values
        variable (_type_): current variable being tested

    Returns:
        _type_: sorted array from
    """
    non_assigned = [
        v for v in problem.variables if v not in assignment and v != variable
    ]
    results = []

    for value in problem.domains[variable]:
        assignment[variable] = value

        deleted_count = 0

        for other_var in non_assigned:
            for other_value in problem.domains[other_var]:
                assignment[other_var] = other_value

                if not problem.is_consistent(assignment):
                    deleted_count += 1

                del assignment[other_var]
        del assignment[variable]
        results.append((value, deleted_count))

    sorted_values = sorted(results, key=lambda x: x[1])

    # NOTE: we return only the values given our currrent
    # contract, but we ca trace the counts for debugging
    return [item[0] for item in sorted_values]
