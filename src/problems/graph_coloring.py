"""
Diego Villalba 12-09-26

Implementation of the graph coloring problem as a csp
"""

from collections import defaultdict

from src.csp.problem import CSP
from src.utils.graph_io import generate_random_graph

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

    return CSP(
        variables=vertices,
        domains=domain,
        is_consistent=_constraint_satisfaction,
    )
