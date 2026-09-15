"""Compares backtracking, the metaheuristic, and OR-Tools on the same graph-
coloring instances: minimum number of colors found and time taken. This is
the "(5 puntos) comparar tiempo de computo y calidad" deliverable.

Reuses find_min_k_backtracking/find_min_k_metaheuristic from run_graph_coloring.py
so the k-search loop isn't duplicated. Nothing to implement here — this file
is glue over things you've already written plus src/integrations/ortools_coloring.py.
"""

from __future__ import annotations

import csv

from _common import load_config, results_path
from run_graph_coloring import (
    ensure_instance,
    find_min_k_backtracking,
    find_min_k_metaheuristic,
)

from src.integrations.ortools_coloring import find_min_colors_ortools
from src.utils.random_seed import set_seed


def main() -> None:
    config = load_config("graph_coloring")
    set_seed(config["seed"])
    # Mismo archivo de sweep que run_graph_coloring.py -- las corridas de
    # ambos scripts se acumulan ahi (append_result_csv nunca sobreescribe).
    sweep_csv_path = results_path("tables", "graph_coloring_k_sweep.csv")

    rows = []
    for instance in config["instances"]:
        num_vertices, edges = ensure_instance(instance, config["seed"])
        name = instance["name"]

        k_bt, _, stats_bt = find_min_k_backtracking(
            num_vertices,
            edges,
            config["k_min"],
            config["k_max"],
            sweep_csv_path,
            f"[{name}/backtracking]",
            **config["backtracking"],
        )
        k_sa, _, stats_sa = find_min_k_metaheuristic(
            num_vertices,
            edges,
            config["k_min"],
            config["k_max"],
            config["seed"],
            sweep_csv_path,
            f"[{name}/metaheuristic]",
            **config["metaheuristic"],
        )
        _, stats_or = find_min_colors_ortools(
            num_vertices,
            edges,
            config["k_min"],
            config["k_max"],
            config["ortools"]["time_limit_seconds"],
        )

        row = {
            "instance": name,
            "num_vertices": num_vertices,
            "num_edges": len(edges),
            "k_backtracking": k_bt,
            "time_backtracking": stats_bt.time_seconds if stats_bt else None,
            "k_metaheuristic": k_sa,
            "time_metaheuristic": stats_sa.time_seconds if stats_sa else None,
            "k_ortools": stats_or.get("k"),
            "time_ortools": stats_or.get("time_seconds"),
        }
        rows.append(row)
        print(row)

    path = results_path("tables", "coloring_comparison.csv")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
