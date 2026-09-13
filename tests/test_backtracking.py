from src.csp.backtracking import backtrack
from src.csp.problem import CSP
from src.problems.australia_coloring import (
    CONSTRAINTS,
    REGIONS,
    australia_coloring_csp,
)


def test_backtrack_colors_australia():
    solution = backtrack(australia_coloring_csp, {})

    assert solution is not None
    assert set(solution) == set(REGIONS)
    for region, neighbors in CONSTRAINTS.items():
        for neighbor in neighbors:
            assert solution[region] != solution[neighbor]


def test_backtrack_returns_none_for_unsatisfiable_csp():
    problem = CSP(
        variables=("A", "B"),
        domains={"A": (1,), "B": (1,)},
        is_consistent=lambda assignment: (
            not (
                "A" in assignment
                and "B" in assignment
                and assignment["A"] == assignment["B"]
            )
        ),
    )

    assignment = {}

    assert backtrack(problem, assignment) is None
    assert assignment == {}


def test_backtrack_tries_another_value_after_a_dead_end():
    def is_consistent(assignment):
        if "A" not in assignment or "B" not in assignment:
            return True
        return assignment["A"] == 2 and assignment["B"] == 1

    problem = CSP(
        variables=("A", "B"),
        domains={"A": (1, 2), "B": (1, 2)},
        is_consistent=is_consistent,
    )

    assert backtrack(problem, {}) == {"A": 2, "B": 1}


def test_backtrack_rejects_an_invalid_complete_assignment():
    def is_consistent(assignment):
        if "A" not in assignment or "B" not in assignment:
            return True
        return assignment["A"] != assignment["B"]

    problem = CSP(
        variables=("A", "B"),
        domains={"A": (1, 2), "B": (1, 2)},
        is_consistent=is_consistent,
    )

    assert backtrack(problem, {"A": 1, "B": 1}) is None
