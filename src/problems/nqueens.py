"""
Diego Villaba 12-09-26

Python implementation of a N-queens CSP problem

inheriting the CSP class to createa na object
"""

from src.csp.problem import CSP

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
