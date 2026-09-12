"""OR-Tools CP-SAT solver for graph coloring — the comparison baseline the
assignment asks for ("Resolver el mismo problema de coloreado de grafos con
OR-Tools, y comparar tiempo de computo y calidad de la solucion").

Mirrors the same "solve for a given k" contract as
src/problems/graph_coloring.py's solve_backtracking/solve_metaheuristic, so
experiments/compare_coloring.py can call all three the same way and the
minimum feasible k found by each method is directly comparable.
"""
from __future__ import annotations

import time

from ortools.sat.python import cp_model


def solve_coloring_ortools(
    num_vertices: int,
    edges: list[tuple[int, int]],
    k: int,
    time_limit_seconds: float = 60.0,
) -> tuple[dict[int, int] | None, dict]:
    """Does a proper coloring with at most `k` colors exist?

    Returns (coloring, stats). coloring is None if none was found within the
    time limit — check stats["status"] to distinguish a proven-infeasible k
    from a timeout (INFEASIBLE vs UNKNOWN).
    """
    model = cp_model.CpModel()
    color = [model.NewIntVar(0, k - 1, f"color_{v}") for v in range(num_vertices)]

    for u, v in edges:
        model.Add(color[u] != color[v])

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_seconds
    start = time.perf_counter()
    status = solver.Solve(model)
    elapsed = time.perf_counter() - start

    stats = {"status": solver.StatusName(status), "time_seconds": elapsed, "k": k}

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        coloring = {v: solver.Value(color[v]) for v in range(num_vertices)}
        return coloring, stats
    return None, stats


def find_min_colors_ortools(
    num_vertices: int,
    edges: list[tuple[int, int]],
    k_min: int = 1,
    k_max: int = 20,
    time_limit_seconds: float = 60.0,
) -> tuple[dict[int, int] | None, dict]:
    """Linear search for the smallest k in [k_min, k_max] with a feasible
    coloring, stopping at the first feasible k found. `time_limit_seconds`
    applies to EACH k tried, not to the whole search."""
    for k in range(k_min, k_max + 1):
        coloring, stats = solve_coloring_ortools(num_vertices, edges, k, time_limit_seconds)
        if coloring is not None:
            stats["k_min_tried"], stats["k_max_tried"] = k_min, k
            return coloring, stats
    return None, {"status": "NO_FEASIBLE_K_IN_RANGE", "k_min_tried": k_min, "k_max_tried": k_max}
