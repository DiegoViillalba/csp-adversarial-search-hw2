"""Example of the testing pattern for this project — mirror this for your
own tests/test_backtracking.py, test_ac3.py, test_minimax.py, etc."""

from src.utils.validation import is_valid_coloring, is_valid_nqueens_solution


def test_four_queens_known_solution_is_valid():
    # column i -> row positions[i]; one classic 4-queens solution
    assert is_valid_nqueens_solution([1, 3, 0, 2])


def test_two_queens_same_row_is_invalid():
    assert not is_valid_nqueens_solution([0, 0])


def test_two_queens_same_diagonal_is_invalid():
    assert not is_valid_nqueens_solution([0, 1])


def test_triangle_is_2_colorable_is_invalid():
    edges = [(0, 1), (1, 2), (0, 2)]
    assert not is_valid_coloring(edges, {0: 0, 1: 1, 2: 0})


def test_triangle_3_coloring_is_valid():
    edges = [(0, 1), (1, 2), (0, 2)]
    assert is_valid_coloring(edges, {0: 0, 1: 1, 2: 2})
