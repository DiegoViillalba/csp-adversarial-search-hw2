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
from src.utils.metrics import append_result_csv, save_solution_json
from src.utils.random_seed import set_seed
from src.utils.validation import is_valid_coloring


def progress_bar(done: int, total: int, width: int = 30) -> str:
    """Text bar, e.g. "[#######-----------] 8/61". Printed as a fresh line per
    k (not a \\r-overwritten one) on purpose: this sweep runs for hours over
    ssh via "nohup ... > logs/run_all.log", and \\r only looks like a real bar
    on a live terminal -- redirected to a file, or watched with `tail -f`,
    the carriage returns just pile up as junk. A new line per k works
    correctly in both places, at the cost of not being a literal animation."""
    filled = int(width * done / total) if total else width
    return f"[{'#' * filled}{'-' * (width - filled)}] {done}/{total}"


def ensure_instance(instance: dict, seed: int) -> tuple[int, list[tuple[int, int]]]:
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


def find_min_k_backtracking(num_vertices, edges, k_min, k_max, sweep_csv_path, label, **kwargs):
    """Same early-stop-at-first-feasible-k search as before, except now every
    attempt (feasible or not) is appended to sweep_csv_path -- stats.extra
    already carries "k" and "timed_out" (see solve_backtracking), so each row
    says whether that k was proven infeasible or just ran out of time,
    instead of only ever seeing the final "min k found" summary. Also prints
    one progress line per k (see progress_bar()'s docstring for why it's not
    a \\r-animated bar)."""
    total = k_max - k_min + 1
    for i, k in enumerate(range(k_min, k_max + 1), start=1):
        coloring, stats = graph_coloring.solve_backtracking(
            num_vertices, edges, k, **kwargs
        )
        append_result_csv(sweep_csv_path, stats)
        if coloring is not None:
            status = "resuelto"
        elif stats.extra.get("timed_out"):
            status = "timeout"
        else:
            status = "infactible"
        print(
            f"  {label} {progress_bar(i, total)} k={k} {status} ({stats.time_seconds:.1f}s)",
            flush=True,
        )
        if coloring is not None:
            return k, coloring, stats
    return None, None, None


def find_min_k_metaheuristic(num_vertices, edges, k_min, k_max, seed, sweep_csv_path, label, **kwargs):
    total = k_max - k_min + 1
    for i, k in enumerate(range(k_min, k_max + 1), start=1):
        coloring, stats = graph_coloring.solve_metaheuristic(
            num_vertices, edges, k, seed=seed, **kwargs
        )
        conflicts = graph_coloring.count_conflicts(edges, coloring)
        append_result_csv(sweep_csv_path, stats)
        print(
            f"  {label} {progress_bar(i, total)} k={k} conflictos={conflicts} ({stats.time_seconds:.1f}s)",
            flush=True,
        )
        if conflicts == 0:
            return k, coloring, stats
    return None, None, None


def main() -> None:
    config = load_config("graph_coloring")
    set_seed(config["seed"])
    csv_path = results_path("tables", "graph_coloring.csv")
    # Archivo NUEVO, separado del de arriba: graph_coloring.csv solo guarda
    # el k ganador de cada metodo/instancia (una fila si tuvo exito). Este
    # registra TODOS los k probados, exitosos o no, para poder evaluar donde
    # exactamente se atoro la busqueda -- nunca se sobreescribe lo que ya
    # habia en graph_coloring.csv.
    sweep_csv_path = results_path("tables", "graph_coloring_k_sweep.csv")

    for instance in config["instances"]:
        num_vertices, edges = ensure_instance(instance, config["seed"])
        name = instance["name"]

        print(f"[{name}] backtracking: buscando k = {config['k_min']}..{config['k_max']}", flush=True)
        k_bt, coloring_bt, stats_bt = find_min_k_backtracking(
            num_vertices,
            edges,
            config["k_min"],
            config["k_max"],
            sweep_csv_path,
            f"[{name}/backtracking]",
            **config["backtracking"],
        )
        if coloring_bt is not None:
            assert is_valid_coloring(edges, coloring_bt)
            append_result_csv(csv_path, stats_bt)
            write_coloring(
                results_path("solutions", f"coloring_{name}_backtracking.txt"),
                coloring_bt,
            )
            # Also as JSON (stats + coloring) alongside the assignment's
            # required .txt format -- experiments/make_plots.py reads this.
            save_solution_json(
                results_path("solutions", f"coloring_{name}_backtracking.json"),
                coloring_bt,
                stats_bt,
            )
        print(f"[{name}] backtracking: min k found = {k_bt}", flush=True)

        print(f"[{name}] metaheuristic: buscando k = {config['k_min']}..{config['k_max']}", flush=True)
        k_sa, coloring_sa, stats_sa = find_min_k_metaheuristic(
            num_vertices,
            edges,
            config["k_min"],
            config["k_max"],
            config["seed"],
            sweep_csv_path,
            f"[{name}/metaheuristic]",
            **config["metaheuristic"],
        )
        if coloring_sa is not None:
            assert is_valid_coloring(edges, coloring_sa)
            append_result_csv(csv_path, stats_sa)
            write_coloring(
                results_path("solutions", f"coloring_{name}_metaheuristic.txt"),
                coloring_sa,
            )
            # extra.energy_history (dropped from the CSV, see as_row()) only
            # survives here -- make_plots.py reads it for convergence plots.
            save_solution_json(
                results_path("solutions", f"coloring_{name}_metaheuristic.json"),
                coloring_sa,
                stats_sa,
            )
        print(f"[{name}] metaheuristic: min k found = {k_sa}", flush=True)


if __name__ == "__main__":
    main()
