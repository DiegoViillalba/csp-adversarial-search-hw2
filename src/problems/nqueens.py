"""
Diego Villaba 12-09-26

Python implementation of a N-queens CSP problem

inheriting the CSP class to createa na object
"""

import time

from src.csp.ac3 import ac3
from src.csp.backtracking import backtrack
from src.csp.heuristics import lcv, mrv
from src.csp.problem import CSP
from src.metaheuristics.simulated_annealing import simulated_annealing
from src.utils.metrics import SearchStats, timer
from src.utils.timeout import time_limit

# _____ Constants in the test problem _____

# Used only for test
N = 4

COLUMNS = tuple(range(N))
ROWS = tuple(range(N))

DOMAINS = {column: ROWS for column in COLUMNS}

# CONSTRAINS is not needed as it'll be encoded
# directly on the satisfaction function


def constraint_satisfaction(assignment: dict[int, int]) -> bool:
    """
    Return whether the movemment is legal or not via:

    1. Not sharing the same row.
    2. Not sharing the same diagonal.

    Expects:
        assignment: dict with the proposal of arangement
    """
    # Edge case , empty assignment
    if assignment == {}:
        return True

    # To avoid coputations and explot python dicts

    move_column = next(reversed(assignment))
    move_row = assignment[move_column]

    for queen_column in assignment.keys() - {move_column}:
        queen_row = assignment[queen_column]

        # Check if they share the same row.
        if move_row == queen_row:
            return False

        # Check if they share the same diagonal.
        row_difference = abs(move_row - queen_row)
        column_difference = abs(move_column - queen_column)

        if row_difference == column_difference:
            return False

    return True


def build_nqueens_csp(n: int) -> CSP:
    """generic builder of nqueens csp

    Args:
        n (int): number of queens

    Returns:
        CSP: Nqueens CSP object
    """
    COLUMNS = tuple(range(n))
    ROWS = tuple(range(n))
    DOMAINS = {column: ROWS for column in COLUMNS}

    return CSP(
        variables=COLUMNS,
        domains=DOMAINS,
        is_consistent=constraint_satisfaction,
    )


# Used only for tests

four_queens_csp = CSP(
    variables=COLUMNS, domains=DOMAINS, is_consistent=constraint_satisfaction
)


# _____ Interface expected by experiments/run_nqueens.py etc _____
# (see README.md "Interfaces esperadas" for the exact contract)


def count_conflicts(positions: list[int]) -> int:
    """Objective function: number of queen pairs attacking each other.

    positions[col] = row of the queen in that column (columns are always
    distinct by construction, so we only need to check row/diagonal).
    """
    n = len(positions)
    conflicts = 0
    for col_a in range(n):
        for col_b in range(col_a + 1, n):
            row_a, row_b = positions[col_a], positions[col_b]
            if row_a == row_b or abs(row_a - row_b) == abs(col_a - col_b):
                conflicts += 1
    return conflicts


def solve_backtracking(
    n: int,
    use_forward_checking: bool,
    use_ac3: bool,
    time_limit_seconds: float | None,
) -> tuple[list[int] | None, SearchStats]:
    """positions[col] = row. None if no solution was found (or time ran out)."""
    problem = build_nqueens_csp(n)

    # AC3 as a preprocessing pass, before backtrack() ever runs. If it
    # empties some column's domain the CSP has no solution at all, so we
    # skip straight to reporting failure instead of searching.
    if use_ac3 and not ac3(problem):
        return None, SearchStats(
            method="backtracking+ac3" + ("+fc" if use_forward_checking else ""),
            problem="nqueens",
            instance_size=n,
            solved=False,
            time_seconds=0.0,
            extra={"reason": "ac3_detected_unsatisfiable"},
        )

    timed_out = False
    solution = None
    with timer() as elapsed:
        try:
            with time_limit(time_limit_seconds):
                solution = backtrack(
                    problem,
                    {},
                    heuristic=mrv,
                    value_order=lcv,
                    forward_checking=use_forward_checking,
                )
        except TimeoutError:
            timed_out = True

    positions = [solution[col] for col in range(n)] if solution else None

    method = "backtracking"
    if use_forward_checking:
        method += "+fc"
    if use_ac3:
        method += "+ac3"

    stats = SearchStats(
        method=method,
        problem="nqueens",
        instance_size=n,
        solved=positions is not None,
        objective=0 if positions is not None else None,
        time_seconds=elapsed(),
        extra={"timed_out": timed_out},
    )
    return positions, stats


def solve_metaheuristic(
    n: int, seed: int | None, **params
) -> tuple[list[int], SearchStats]:
    """Best assignment found (may still have conflicts — check stats.objective)."""
    problem = build_nqueens_csp(n)

    with timer() as elapsed:
        assignment, cost, energy_history = simulated_annealing(problem, seed=seed, **params)

    positions = [assignment[col] for col in range(n)]

    stats = SearchStats(
        method="simulated_annealing",
        problem="nqueens",
        instance_size=n,
        solved=cost == 0,
        objective=cost,
        time_seconds=elapsed(),
        extra={
            "energy_history": energy_history,
            **{k: v for k, v in params.items() if k != "time_limit_seconds"},
        },
    )
    return positions, stats


def enumerate_solutions(
    n: int, max_solutions: int | None, time_limit_seconds: float | None
) -> tuple[list[list[int]], SearchStats]:
    """All solutions found until the first limit is hit.

    stats.extra["exhaustive"]: True iff the search finished on its own
    (not cut off by max_solutions/time_limit_seconds).

    This is a small dedicated recursive search rather than a reuse of
    backtrack(): the generic engine returns the FIRST solution and stops,
    it has no notion of "keep going and collect every solution up to a
    cap" — that behavior is specific enough to this function that it isn't
    worth bolting onto src/csp/backtracking.py. It still reuses
    constraint_satisfaction, so the actual N-queens rule lives in one place.
    """
    solutions: list[list[int]] = []
    assignment: dict[int, int] = {}
    start = time.perf_counter()
    exhaustive = True

    def limit_reached() -> bool:
        nonlocal exhaustive
        if max_solutions is not None and len(solutions) >= max_solutions:
            exhaustive = False
            return True
        if (
            time_limit_seconds is not None
            and time.perf_counter() - start > time_limit_seconds
        ):
            exhaustive = False
            return True
        return False

    def place(col: int) -> None:
        if limit_reached():
            return
        if col == n:
            solutions.append([assignment[c] for c in range(n)])
            return
        for row in range(n):
            assignment[col] = row
            if constraint_satisfaction(assignment):
                place(col + 1)
            del assignment[col]
            if limit_reached():
                return

    place(0)

    stats = SearchStats(
        method="backtracking_enumeration",
        problem="nqueens",
        instance_size=n,
        solved=len(solutions) > 0,
        objective=len(solutions),
        time_seconds=time.perf_counter() - start,
        extra={"exhaustive": exhaustive, "max_solutions": max_solutions},
    )
    return solutions, stats
