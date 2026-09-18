""" Diego Villalba 16-09-26
Independent solution checkers. Made so validation chekcing is
"""

from __future__ import annotations

from collections.abc import Iterable


def is_valid_nqueens_solution(positions) -> bool:
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


def is_valid_coloring(
    edges: Iterable[tuple[int, int]], coloring: dict[int, int]
) -> bool:
    """coloring maps vertex -> color id. Checks every edge's endpoints differ,
    and that every endpoint appearing in `edges` has an assigned color."""
    for u, v in edges:
        if u not in coloring or v not in coloring:
            return False
        if coloring[u] == coloring[v]:
            return False
    return True
