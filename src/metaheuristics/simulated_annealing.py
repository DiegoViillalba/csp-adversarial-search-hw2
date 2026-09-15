"""
Diego Villalba 12-09-26

Simulated annealing over a CSP: local search on complete assignments that
accepts worsening moves with a probability that shrinks as the
"temperature" cools, so it can escape local minima early on and settles
into one late on.

NOTE: count_conflicts is O(num_variables^2) per call since CSP has no
explicit neighbor structure to restrict the pairwise check to. On the
1000-node coloring instance this means fewer iterations complete within a
given time budget than a version with an incremental, neighbor-aware delta
would manage. Left as-is given the time we have; time_limit_seconds keeps
it from running forever.
"""

import math
import random
import time

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
       NOTE: We used unique edge traversal to speed up computing
    Args:
        problem (CSP): CSP object
        assignment (dict): a COMPLETE assignment, variable -> value

    Returns:
        int: number of conflicting pairs (0 means `assignment` is a solution)
    """
    conflicts = 0


    if problem.neighbors:
        for v in problem.variables:
            for n in problem.neighbors[v]:
                if n > v:
                    pair = {v: assignment[v], n: assignment[n]}

                    if not problem.is_consistent(pair):
                        conflicts += 1

    else:

        for i, xi in enumerate(problem.variables):
            for xj in problem.variables[i + 1 :]:
                
                pair = {xi: assignment[xi], xj: assignment[xj]}
                
                if not problem.is_consistent(pair):
                    conflicts += 1


    return conflicts


# NOTE: This implementation was realized after the previous one

def conflicts_for_variable(problem: CSP, assignment: dict, variable) -> int:
    """Count conflicts involving just `variable`, under its CURRENT value in
    `assignment`, checked only against its neighbors (or every other
    variable if `problem.neighbors` is None). Changing one variable can only
    ever affect constraints touching it -- every other pair is unaffected --
    so this is all `random_neighbor` needs to compute a delta instead of
    paying for a full `count_conflicts` recount on every iteration.

    Args:
        problem (CSP): CSP object
        assignment (dict): a COMPLETE assignment, variable -> value
        variable: the variable to check

    Returns:
        int: number of neighbors (or other variables) currently conflicting
            with `variable`'s value
    """
    others = (
        problem.neighbors[variable]
        if problem.neighbors
        else (v for v in problem.variables if v != variable)
    )

    conflicts = 0
    for other in others:
        pair = {variable: assignment[variable], other: assignment[other]}
        if not problem.is_consistent(pair):
            conflicts += 1

    return conflicts


def random_neighbor(problem: CSP, assignment: dict, rng: random.Random) -> tuple:
    """Move ONE randomly chosen variable to a new value, MUTATING `assignment`
    in place instead of returning a copy (avoids allocating a full extra
    assignment on every iteration of simulated_annealing), and reporting
    exactly how much this one move changed the total conflict count.

    Args:
        problem (CSP): CSP object
        assignment (dict): current COMPLETE assignment, mutated in place
        rng (random.Random): random number generator, for reproducibility

    Returns:
        tuple[dict, tuple | None, int]: (assignment, undo_info, delta).
            `assignment` is the SAME object passed in, now mutated.
            `undo_info` is (variable, old_value) so the caller can revert
            the move later with `assignment[variable] = old_value` — or
            None if the chosen variable had no other value to try (nothing
            was mutated, delta is 0). `delta` is how much the TOTAL conflict
            count changed because of this move (negative = improved) --
            add it to the caller's running cost instead of recomputing
            count_conflicts from scratch.
    """

    random_variable = rng.choice(problem.variables)
    current_value = assignment[random_variable]

    elegible_values = [
        v for v in problem.domains[random_variable]
        if v != current_value
    ]

    if not elegible_values:
        return assignment, None, 0

    conflicts_before = conflicts_for_variable(problem, assignment, random_variable)

    assignment[random_variable] = rng.choice(elegible_values)

    conflicts_after = conflicts_for_variable(problem, assignment, random_variable)

    delta = conflicts_after - conflicts_before

    return assignment, (random_variable, current_value), delta




# ____ Main implementation ______

def simulated_annealing(
    problem: CSP,
    initial_temperature: float = 10.0,
    cooling_rate: float = 0.995,
    max_iterations: int = 100_000,
    time_limit_seconds: float | None = None,
    seed: int | None = None,
) -> tuple[dict, int]:
    """
    Search for a zero-conflict assignment via simulated annealing. (Recocido
    Simulado). Main refrence:
    https://inst.eecs.berkeley.edu/~cs188/textbook/csp/local-search.html

    Args:
        problem (CSP): CSP object
        initial_temperature (float): starting temperature, higher means more
            tolerance for worsening moves early on
        cooling_rate (float): multiplies the temperature after every
            iteration, must be in (0, 1)
        max_iterations (int): hard cap on iterations, in case a 0-conflict
            assignment is never reached
        time_limit_seconds (float | None): wall-clock budget, checked once
            per iteration; None means no time limit
        seed (int | None): random seed, for reproducibility

    Returns:
        tuple[dict, int]: the best assignment found and its conflict count
            (0 means a real solution was found, not just the best attempt)
    """
    # rng for  reproducibility
    rng = random.Random(seed)
    start_time = time.perf_counter()

    current = random_complete_assignment(problem, rng)
    current_cost = count_conflicts(problem, current)

    # `best` MUST be an independent copy, not `current` itself 
    best, best_cost = dict(current), current_cost
    temperature = initial_temperature

    for _ in range(max_iterations):
        if best_cost == 0:
            break

        if (
            time_limit_seconds is not None
            and time.perf_counter() - start_time > time_limit_seconds
        ):
            break


        current, old_state, delta = random_neighbor(problem, current, rng)

        if old_state is None:
            continue

        # Metropolis acceptance: always keep improving moves; keep a
        # worsening one too, with probability exp(-delta/temperature).
        if delta < 0 or rng.random() < math.exp(-delta / temperature):
            current_cost = current_cost + delta

            if current_cost < best_cost:
                best, best_cost = dict(current), current_cost
        else:
            variable, old_value = old_state
            current[variable] = old_value

        temperature = max(temperature * cooling_rate, 1e-10)

    return best, best_cost


        