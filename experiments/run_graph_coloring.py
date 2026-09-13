"""Solves graph coloring with backtracking and with the metaheuristic, for
every instance in configs/graph_coloring.yaml, searching k = k_min..k_max
for the smallest k each method solves with zero conflicts.

Expects src/problems/graph_coloring.py to expose:
    solve_backtracking(num_vertices, edges, k, use_forward_checking, use_ac3,
                        time_limit_seconds) -> (coloring | None, SearchStats)
    solve_metaheuristic(num_vertices, edges, k, seed, **params)
                        -> (coloring, SearchStats)   # coloring may still have conflicts
    count_conflicts(edges, coloring) -> int
See README.md ("Interfaces esperadas") for the full contract.
"""

from __future__ import annotations

from _common import REPO_ROOT, load_config, results_path

from src.problems import graph_coloring
from src.utils.graph_io import (
    generate_random_graph,
    read_graph,
    write_coloring,
    write_graph,
)
from src.utils.metrics import append_result_csv
from src.utils.random_seed import set_seed
from src.utils.validation import is_valid_coloring


def ensure_instance(
    instance: dict, seed: int
) -> tuple[int, list[tuple[int, int]]]:
    """Reads instance["path"], generating a random instance there first if it
    doesn't exist yet, so `python run_graph_coloring.py` works out of the box."""
    path = REPO_ROOT / instance["path"]
    if not path.exists():
        num_vertices, edges = generate_random_graph(
            instance["num_vertices"], instance["edge_prob"], seed=seed
        )
        write_graph(path, num_vertices, edges)
        print(f"generated {path} ({num_vertices} vertices, {len(edges)} edges)")
    return read_graph(path)


def find_min_k_backtracking(num_vertices, edges, k_min, k_max, **kwargs):
    for k in range(k_min, k_max + 1):
        coloring, stats = graph_coloring.solve_backtracking(
            num_vertices, edges, k, **kwargs
        )
        if coloring is not None:
            return k, coloring, stats
    return None, None, None


def find_min_k_metaheuristic(num_vertices, edges, k_min, k_max, seed, **kwargs):
    for k in range(k_min, k_max + 1):
        coloring, stats = graph_coloring.solve_metaheuristic(
            num_vertices, edges, k, seed=seed, **kwargs
        )
        if graph_coloring.count_conflicts(edges, coloring) == 0:
            return k, coloring, stats
    return None, None, None


def main() -> None:
    config = load_config("graph_coloring")
    set_seed(config["seed"])
    csv_path = results_path("tables", "graph_coloring.csv")

    for instance in config["instances"]:
        num_vertices, edges = ensure_instance(instance, config["seed"])
        name = instance["name"]

        k_bt, coloring_bt, stats_bt = find_min_k_backtracking(
            num_vertices,
            edges,
            config["k_min"],
            config["k_max"],
            **config["backtracking"],
        )
        if coloring_bt is not None:
            assert is_valid_coloring(edges, coloring_bt)
            append_result_csv(csv_path, stats_bt)
            write_coloring(
                results_path("solutions", f"coloring_{name}_backtracking.txt"),
                coloring_bt,
            )
        print(f"[{name}] backtracking: min k found = {k_bt}")

        k_sa, coloring_sa, stats_sa = find_min_k_metaheuristic(
            num_vertices,
            edges,
            config["k_min"],
            config["k_max"],
            config["seed"],
            **config["metaheuristic"],
        )
        if coloring_sa is not None:
            assert is_valid_coloring(edges, coloring_sa)
            append_result_csv(csv_path, stats_sa)
            write_coloring(
                results_path("solutions", f"coloring_{name}_metaheuristic.txt"),
                coloring_sa,
            )
        print(f"[{name}] metaheuristic: min k found = {k_sa}")


if __name__ == "__main__":
    main()
