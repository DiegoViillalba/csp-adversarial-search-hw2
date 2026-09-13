"""
Diego Villalba 12-09-26

Shared building blocks for local search metaheuristics over a CSP. Unlike
backtracking (which builds a PARTIAL assignment one variable at a time),
these work over a COMPLETE assignment from the start, searching for one
with the fewest constraint violations.
"""

import random

from src.csp.problem import CSP

# ____ Helper Functions ____


def random_complete_assignment(problem: CSP, rng: random.Random) -> dict:
    """Build a random assignment covering every variable, ignoring constraints.

    Args:
        problem (CSP): CSP object
        rng (random.Random): random number generator, for reproducibility

    Returns:
        dict: variable -> value, one randomly chosen value per variable
    """
    return {
        variable: rng.choice(problem.domains[variable])
        for variable in problem.variables
    }


def count_conflicts(problem: CSP, assignment: dict) -> int:
    """Count how many pairs of variables violate a constraint under `assignment`.

    Args:
        problem (CSP): CSP object
        assignment (dict): a COMPLETE assignment, variable -> value

    Returns:
        int: number of conflicting pairs (0 means `assignment` is a solution)
    """
    variables = list(problem.variables)
    conflicts = 0

    for i, xi in enumerate(variables):
        for xj in variables[i + 1 :]:
            pair = {xi: assignment[xi], xj: assignment[xj]}
            if not problem.is_consistent(pair):
                conflicts += 1

    return conflicts


def random_neighbor(problem: CSP, assignment: dict, rng: random.Random) -> dict:
    """Produce a neighboring assignment: `assignment` with one randomly chosen
    variable moved to a new, randomly chosen value from its domain.

    Args:
        problem (CSP): CSP object
        assignment (dict): current COMPLETE assignment
        rng (random.Random): random number generator, for reproducibility

    Returns:
        dict: a new assignment, differing from `assignment` in one variable
    """
    neighbor = dict(assignment)
    variable = rng.choice(problem.variables)
    neighbor[variable] = rng.choice(problem.domains[variable])
    return neighbor
