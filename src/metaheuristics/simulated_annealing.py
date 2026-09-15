"""
Diego Villalba 12-09-26

Simulated annealing over a CSP: local search on complete assignments that
accepts worsening moves with a probability that shrinks as the
"temperature" cools, so it can escape local minima early on and settles
into one late on.

NOTE: count_conflicts is O(num_variables^2) per call (see
src/metaheuristics/base.py) since CSP has no explicit neighbor structure to
restrict the pairwise check to. On the 1000-node coloring instance this
means fewer iterations complete within a given time budget than a version
with an incremental, neighbor-aware delta would manage. Left as-is given
the time we have; time_limit_seconds keeps it from running forever.
"""

import math
import random
import time

from src.csp.problem import CSP
from src.metaheuristics.base import (
    count_conflicts,
    random_complete_assignment,
    random_neighbor,
)

# ____ Helper Functions ____


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
