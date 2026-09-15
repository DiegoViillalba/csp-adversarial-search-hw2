"""Overnight, no-heuristics run of graph-coloring backtracking on the
1000-node instance: use_forward_checking=False, use_ac3=False. Contrasts
against run_graph_coloring.py's optimized run (FC+AC3 on, finds k=8 in
~8.5s -- see results/tables/graph_coloring.csv) to show, empirically, how
much those two prunings are worth on a real instance. Exploratory, not one
of the assignment's required deliverables.

Targets K=8 specifically (the minimum the optimized backtracking already
found feasible for this instance) rather than searching k_min..k_max, so
the whole time budget goes into a single, known-feasible attempt instead
of being split across up to 11 values of k.

TIME_LIMIT_SECONDS is hardcoded here rather than read from
configs/graph_coloring.yaml on purpose: that config is shared with the
regular, fast pipeline (run_graph_coloring.py / compare_coloring.py /
scripts/run_remote_heavy.sh), and bumping it there would make every
normal run take up to 55 hours too.

Writes to *_overnight.csv/.json filenames so this never collides with or
overwrites results/tables/graph_coloring.csv from the regular run.
"""

from __future__ import annotations

from _common import load_config, results_path
from run_graph_coloring import ensure_instance

from src.problems import graph_coloring
from src.utils.metrics import append_result_csv, save_solution_json
from src.utils.validation import is_valid_coloring

TIME_LIMIT_SECONDS = 55 * 3600  # 55 horas
K = 8


def main() -> None:
    config = load_config("graph_coloring")
    large = config["instances"][1]
    num_vertices, edges = ensure_instance(large, config["seed"])

    coloring, stats = graph_coloring.solve_backtracking(
        num_vertices,
        edges,
        K,
        use_forward_checking=False,
        use_ac3=False,
        time_limit_seconds=TIME_LIMIT_SECONDS,
    )

    append_result_csv(results_path("tables", "graph_coloring_overnight.csv"), stats)
    if coloring is not None:
        assert is_valid_coloring(edges, coloring)
        save_solution_json(
            results_path(
                "solutions", "coloring_large_backtracking_naive_overnight.json"
            ),
            coloring,
            stats,
        )

    print(
        f"k={K} (naive, sin FC/AC3): solved={stats.solved} "
        f"time={stats.time_seconds:.2f}s"
    )


if __name__ == "__main__":
    main()
