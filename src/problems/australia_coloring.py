"""
Diego Villalba

Australian map coloring represented as a CSP.
Builded as a problem to test the gneral implementation of
backtracking
"""

from src.csp.problem import CSP

# ____ Constants in the problem ____

REGIONS = ("WA", "NT", "SA", "Q", "NSW", "V", "T")

COLORS = ("R", "G", "B")

DOMAINS = {region: COLORS for region in REGIONS}

CONSTRAINTS = {
    "WA": ("NT", "SA"),
    "NT": ("SA", "Q"),
    "SA": ("Q", "NSW", "V"),
    "Q": ("NSW",),
    "NSW": ("V",),
}


def constraint_satisfaction(assignment: dict[str, str]) -> bool:
    """Return whether all adjacent assigned regions have different colors."""

    for region, neighbors in CONSTRAINTS.items():
        if region not in assignment:
            continue

        for neighbor in neighbors:
            if neighbor in assignment and assignment[region] == assignment[neighbor]:
                return False

    return True


australia_coloring_csp = CSP(
    variables=REGIONS,
    domains=DOMAINS,
    is_consistent=constraint_satisfaction,
)
