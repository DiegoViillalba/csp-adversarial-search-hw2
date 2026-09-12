"""Independent solution checkers.

These do NOT reimplement the objective/cost function your solvers optimize
(that is yours to define, per problem, as the assignment asks). They exist
so tests and experiment runners can sanity-check a solver's output without
trusting the solver's own bookkeeping.
"""
from __future__ import annotations

from collections.abc import Iterable


def is_valid_nqueens_solution(positions: list[int]) -> bool:
    """positions[col] = row of the queen in that column. Checks no two queens
    share a row or a diagonal (columns are distinct by construction)."""
    n = len(positions)
    for col_a in range(n):
        for col_b in range(col_a + 1, n):
            row_a, row_b = positions[col_a], positions[col_b]
            if row_a == row_b:
                return False
            if abs(row_a - row_b) == abs(col_a - col_b):
                return False
    return True


def is_valid_coloring(edges: Iterable[tuple[int, int]], coloring: dict[int, int]) -> bool:
    """coloring maps vertex -> color id. Checks every edge's endpoints differ,
    and that every endpoint appearing in `edges` has an assigned color."""
    for u, v in edges:
        if u not in coloring or v not in coloring:
            return False
        if coloring[u] == coloring[v]:
            return False
    return True
