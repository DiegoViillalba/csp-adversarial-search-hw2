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
    # Deliberately does NOT check is_consistent here — this is the starting
    # point for local search, which is allowed (expected, even) to start
    # from a state full of conflicts and improve from there.
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

    # Check every UNORDERED pair exactly once (xj only ranges over variables
    # AFTER xi in the list) — same 2-entry-dict trick as ac3.revise, just
    # applied to every pair instead of stopping at the first support found.
    # NOTE: this is O(num_variables^2) is_consistent calls per call to
    # count_conflicts — fine at N=100, expensive at 1000 nodes (see the
    # module NOTE above).
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
    # dict(assignment) makes a shallow COPY — mutating `neighbor` below
    # never touches the caller's `assignment`. Needed because simulated
    # annealing keeps the current state around to compare against.
    neighbor = dict(assignment)
    variable = rng.choice(problem.variables)
    # The new value can, by chance, be the same as the old one — that's
    # fine, it just means this particular move happens to be a no-op.
    neighbor[variable] = rng.choice(problem.domains[variable])
    return neighbor


def simulated_annealing(
    problem: CSP,
    initial_temperature: float = 10.0,
    cooling_rate: float = 0.995,
    max_iterations: int = 100_000,
    time_limit_seconds: float | None = None,
    seed: int | None = None,
) -> tuple[dict, int]:
    """Search for a zero-conflict assignment via simulated annealing.

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
    rng = random.Random(seed)
    start_time = time.perf_counter()

    # `current` is where the random walk is right now (can get worse).
    # `best`/`best_cost` separately track the best state EVER seen, since
    # simulated annealing is allowed to wander away from a good state and
    # we don't want to lose it if that happens.
    current = random_complete_assignment(problem, rng)
    current_cost = count_conflicts(problem, current)

    best, best_cost = current, current_cost
    temperature = initial_temperature

    for _ in range(max_iterations):
        if best_cost == 0:
            # Already found an actual solution — no point in continuing.
            break

        if (
            time_limit_seconds is not None
            and time.perf_counter() - start_time > time_limit_seconds
        ):
            # Ran out of time — return whatever's best so far (this
            # function is "anytime": it degrades gracefully, it doesn't
            # just fail like backtrack does when it can't finish).
            break

        neighbor = random_neighbor(problem, current, rng)
        neighbor_cost = count_conflicts(problem, neighbor)

        # Negative delta = neighbor has FEWER conflicts = strictly better.
        delta = neighbor_cost - current_cost

        # Metropolis acceptance rule: always take improving moves; take a
        # worsening move too, but only with probability exp(-delta/T).
        # Bigger delta (much worse) or lower temperature (later in the run)
        # both push that probability toward 0 — early on, hot, we wander
        # more freely; late, cold, we mostly only accept improvements.
        if delta < 0 or rng.random() < math.exp(-delta / temperature):
            current, current_cost = neighbor, neighbor_cost

            if current_cost < best_cost:
                best, best_cost = current, current_cost

        # Cool down a little every iteration. The 1e-10 floor exists only
        # to avoid a division by zero in exp(-delta/temperature) above if
        # cooling_rate/max_iterations ever drove it all the way to 0.
        temperature = max(temperature * cooling_rate, 1e-10)

    return best, best_cost
