"""
Diego Villalba 12-09-26

Shared representation for finite constraint satisfaction problems.
"""

from collections.abc import Callable, Hashable, Iterable


class CSP:
    """Generic representation of a finite constraint satisfaction problem.

    Bundles the three pieces every solver in this project needs (variables,
    domains, and a constraint checker) without deciding how to search for a
    solution.

    Attributes:
        variables (tuple): every variable in the problem, in a fixed order
            (e.g. used by backtracking's default "first unassigned" ordering).
        domains (dict): variable -> tuple of legal values. Mutated in place
            by ac3()/forward_check() while pruning, and put back by
            restore_domains().
        is_consistent (Callable): given a partial or complete assignment
            (dict, variable -> value), returns whether it's consistent. By
            convention (see ac3.py, forward_checking.py, backtracking.py)
            it only needs to check the constraints touching the
            LAST-inserted key of the dict it's handed.
        neighbors (dict | None): optional adjacency, variable -> the other
            variables it's actually constrained with. None means "unknown"
            -- ac3() then falls back to treating every pair of variables as
            a candidate arc. Set this explicitly (build_graph_coloring_csp
            does) to skip that O(len(variables)^2) fallback on problems
            where most variable pairs never constrain each other.
    """

    def __init__(
        self,
        variables: tuple,
        domains: dict,
        is_consistent: Callable
    ) -> None:
        """Build a CSP.

        Args:
            variables (tuple): every variable in the problem, in a fixed order.
            domains (dict): variable -> tuple of legal values.
            is_consistent (Callable): constraint-checking function, see the
                class docstring for the "last-inserted key" convention it
                must follow.
        """
        self.variables = variables
        self.domains = domains
        self.is_consistent = is_consistent
        self.neighbors: dict[Hashable, Iterable[Hashable]] | None = None

        # neighbors: Optional adjacency (var -> iterable of vars constrained
        # together). None means "unknown" -- ac3() falls back to treating
        # every pair of variables as a candidate arc. Set explicitly (e.g.
        # by build_graph_coloring_csp) to skip that O(V^2) fallback on
        # sparse problems.

    def describe(self) -> None:
        """Print a short summary of the problem.

        Prints the variables and their domains as-is, for quick manual
        inspection
        """
        print("CSP \n")
        print("Variables:", self.variables)
        print("Domains:", self.domains)
