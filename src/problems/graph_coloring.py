"""
Diego Villalba 12-09-26

Implementation of the graph coloring problem as a csp
"""

from collections import defaultdict

from src.csp.ac3 import ac3
from src.csp.backtracking import backtrack
from src.csp.heuristics import lcv, mrv
from src.csp.problem import CSP
from src.metaheuristics.simulated_annealing import simulated_annealing
from src.utils.graph_io import generate_random_graph
from src.utils.metrics import SearchStats, timer
from src.utils.timeout import time_limit

# _____ Constants for the test problem. _____

N = 10
VERTICES = tuple(range(N))
K = 3

# build a similar graph to the australia one to keep validations
_, EDGES = generate_random_graph(N, edge_prob=0.5, seed=1)


def build_constraints(edges: list, num_vertices: int) -> dict:
    """Build de ajacency dictionary per vertex

    Args:
        edges (list): list containing all the edges as tuples
        num_vertices (int): number fo vertex

    Returns:
        dict: Adjacecy vertex dictionary
    """
    adj_dict = defaultdict(set)

    # We'll use a set to fast queryng
    for v in range(num_vertices):
        adj_dict[v] = set()

    # NOTE: Considering bi directional graphs
    for edge in edges:
        u, v = edge
        adj_dict[u].add(v)
        adj_dict[v].add(u)

    return dict(adj_dict)


def build_graph_coloring_csp(vertex_num: int, edges: list, k: int) -> CSP:
    """General builder for graph coloring
    This function recieves arguments defined by the
    generate_random_graph function in src.utils.graph_io

    Args:
        vertex_num (int): Number of verteces in the graph
        edges (list): list with tuples of verteces (admits directional graphs)
        k (int): number od colors per vertex
    Returns:
        CSP: _description_
    """

    vertices = tuple(range(vertex_num))

    domain = {v: tuple(range(k)) for v in vertices}

    adjacency = build_constraints(edges, vertex_num)

    def _constraint_satisfaction(assignment: dict[int, int]) -> bool:
        """Contrain satisfaction function

        Args:
            assignment (dict[int,int]): Current node-color assignment

        Returns:
            bool: whether the assignment is valid or not
        """
        if assignment == {}:
            return True

        last_vertex = next(reversed(assignment))
        last_color = assignment[last_vertex]
        neightbors = adjacency[last_vertex]

        for neightbor in neightbors:
            if neightbor in assignment and assignment[neightbor] == last_color:
                return False

        return True

    csp = CSP(
        variables=vertices,
        domains=domain,
        is_consistent=_constraint_satisfaction,
    )

    # adding the optiional call for this cases
    csp.neighbors = adjacency

    return csp


# _____ Interface expected by experiments/run_graph_coloring.py etc _____
# (see README.md "Interfaces esperadas" for the exact contract)


def count_conflicts(edges: list, coloring: dict[int, int]) -> int:
    """Objective function: number of edges whose endpoints share a color."""
    return sum(1 for u, v in edges if coloring.get(u) == coloring.get(v))


def solve_backtracking(
    num_vertices: int,
    edges: list[tuple[int, int]],
    k: int,
    use_forward_checking: bool,
    use_ac3: bool,
    time_limit_seconds: float | None,
):
    """Own coloring with exactly k colors, or None if infeasible / timed out."""
    problem = build_graph_coloring_csp(num_vertices, edges, k)

    if use_ac3 and not ac3(problem):
        return None, SearchStats(
            method="backtracking+ac3" + ("+fc" if use_forward_checking else ""),
            problem="graph_coloring",
            instance_size=num_vertices,
            solved=False,
            time_seconds=0.0,
            extra={"k": k, "reason": "ac3_detected_unsatisfiable"},
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

    coloring = dict(solution) if solution else None

    method = "backtracking"
    if use_forward_checking:
        method += "+fc"
    if use_ac3:
        method += "+ac3"

    stats = SearchStats(
        method=method,
        problem="graph_coloring",
        instance_size=num_vertices,
        solved=coloring is not None,
        objective=0 if coloring is not None else None,
        time_seconds=elapsed(),
        extra={"k": k, "timed_out": timed_out},
    )
    return coloring, stats


def solve_metaheuristic(
    num_vertices: int,
    edges: list[tuple[int, int]],
    k: int,
    seed: int | None,
    **params,
):
    """Best coloring found using exactly k colors (may still have conflicts
    — check stats.objective)."""
    problem = build_graph_coloring_csp(num_vertices, edges, k)

    with timer() as elapsed:
        assignment, cost, energy_history = simulated_annealing(problem, seed=seed, **params)

    stats = SearchStats(
        method="simulated_annealing",
        problem="graph_coloring",
        instance_size=num_vertices,
        solved=cost == 0,
        objective=cost,
        time_seconds=elapsed(),
        extra={
            "k": k,
            "energy_history": energy_history,
            **{k_: v for k_, v in params.items() if k_ != "time_limit_seconds"},
        },
    )
    return dict(assignment), stats
