"""
Diego Villaba 12-09-26

Python implementation of a N-queens CSP problem

inheriting the CSP class to createa na object
"""

import time
from collections.abc import Callable

from src.csp.ac3 import ac3
from src.csp.backtracking import backtrack
from src.csp.heuristics import lcv, mrv
from src.csp.problem import CSP
from src.metaheuristics.simulated_annealing import simulated_annealing
from src.utils.metrics import SearchStats, timer
from src.utils.recursion import deeper_recursion
from src.utils.resources import peak_memory_mb
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
    # empties some column's domain the CSP has no solution so skip

    if use_ac3:
        activation_ac3 = ac3(problem)
        if not activation_ac3:
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
    node_counter = [0]

    # Using context mannagers to be careful with recursion
    # https://medium.com/analytics-vidhya/increase-maximum-recursion-depth-in-python-using-context-manager-1c67eaf4e71b
    with timer() as elapsed:
        try:
            with time_limit(time_limit_seconds), deeper_recursion(n + 200):
                solution = backtrack(
                    problem,
                    {},
                    heuristic=mrv,
                    value_order=lcv,
                    forward_checking=use_forward_checking,
                    node_counter=node_counter,
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
        nodes_expanded=node_counter[0],
        time_seconds=elapsed(),
        extra={"timed_out": timed_out, "peak_memory_mb": peak_memory_mb()},
    )
    return positions, stats


def enumerate_solutions(
    n: int = 8,
    max_solutions: int | None = None,
    time_limit_seconds: float | None = 30.0,
    use_forward_checking: bool = True,
    use_ac3: bool = True,
) -> tuple[list[list[int]], SearchStats]:
    """All solutions found until the first limit is hit.

    stats.extra["exhaustive"]: True iff the search finished on its own
    (not cut off by max_solutions/time_limit_seconds).

    Reuses the generic backtrack engine with find_all=True, incorporating
    time limits and allowing heuristic/forward_checking configurations.
    """
    # Create the CSP problem instance for N-queens
    problem = build_nqueens_csp(n)

    # Apply AC-three preprocessing if requested
    if use_ac3:
        ac3(problem)

    node_counter = [0]
    start = time.perf_counter()
    exhaustive = True
    
    # NEW: The accumulator list that backtrack will safely update in real-time
    solutions_dicts = []

    try:
        # Using context managers to handle limits and recursion depth
        with time_limit(time_limit_seconds), deeper_recursion(n + 200):
            backtrack(
                problem=problem,
                assignment={},
                heuristic=mrv,
                value_order=lcv,
                forward_checking=use_forward_checking,
                node_counter=node_counter,
                find_all=True,
                solutions_accumulator=solutions_dicts,  # Passed by reference
            )
    except Exception:
        # Timeout or recursion error reached; the search was cut off.
        # solutions_dicts already contains all solutions found right up to the cutoff.
        exhaustive = False

    # Convert the assignment dictionaries into the expected list of integers format
    solutions: list[list[int]] = []
    for sol_dict in solutions_dicts:
        if max_solutions is not None and len(solutions) >= max_solutions:
            exhaustive = False
            break
        solutions.append([sol_dict[c] for c in range(n)])

    # Mark as non-exhaustive if total solutions exceed the maximum allowed limit
    if max_solutions is not None and len(solutions_dicts) > max_solutions:
        exhaustive = False

    # Determine solved status (False if cut off by timeout or max_solutions)
    is_solved = False if not exhaustive else (len(solutions) > 0)

    stats = SearchStats(
        method="backtracking_enumeration",
        problem="nqueens",
        instance_size=n,
        solved=is_solved,
        objective=len(solutions),
        nodes_expanded=node_counter[0],
        time_seconds=time.perf_counter() - start,
        extra={
            "exhaustive": exhaustive,
            "max_solutions": max_solutions,
            "peak_memory_mb": peak_memory_mb(),
        },
    )
    return solutions, stats

def solve_metaheuristic(
    n: int, seed: int | None, **params
) -> tuple[list[int], SearchStats]:
    """Best assignment found (may still have conflicts — check stats.objective)."""
    problem = build_nqueens_csp(n)

    with timer() as elapsed:
        assignment, cost, energy_history = simulated_annealing(
            problem, seed=seed, **params
        )

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
            "peak_memory_mb": peak_memory_mb(),
            **{k: v for k, v in params.items() if k != "time_limit_seconds"},
        },
    )
    return positions, stats