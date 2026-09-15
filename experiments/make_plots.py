"""Builds every figure the report needs from results/, so they're ready as
soon as the experiments finish -- run last in scripts/run_remote_heavy.sh
(and after experiments/run_*.py locally, e.g. from notebooks/local_results.ipynb).

Reads:
    results/tables/nqueens.csv             (run_nqueens.py)
    results/tables/graph_coloring.csv       (run_graph_coloring.py)
    results/tables/coloring_comparison.csv  (compare_coloring.py)
    results/solutions/*_metaheuristic.json  (energy_history, for convergence plots)

Writes PNGs into report/figures/, referenced from report/sections/*.tex.
Silently skips any figure whose input file doesn't exist yet (e.g. if only
some experiments have been run), so this is always safe to re-run.
"""

from __future__ import annotations

import csv
import json

import matplotlib

matplotlib.use("Agg")  # headless -- no display on the remote server
import matplotlib.pyplot as plt

from _common import REPO_ROOT, results_path

FIGURES_DIR = REPO_ROOT / "report" / "figures"


def _read_csv(path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def _read_json(path) -> dict | None:
    if not path.exists():
        return None
    with path.open() as f:
        return json.load(f)


def _save(fig, name: str) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / name
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {path}")


def plot_nqueens_time() -> None:
    rows = _read_csv(results_path("tables", "nqueens.csv"))
    if not rows:
        return

    sizes = sorted({int(r["instance_size"]) for r in rows})
    bt_times = [
        next(
            (
                float(r["time_seconds"])
                for r in rows
                if int(r["instance_size"]) == n
                and r["method"].startswith("backtracking")
            ),
            None,
        )
        for n in sizes
    ]
    sa_times = [
        next(
            (
                float(r["time_seconds"])
                for r in rows
                if int(r["instance_size"]) == n and r["method"] == "simulated_annealing"
            ),
            None,
        )
        for n in sizes
    ]

    x = range(len(sizes))
    width = 0.35
    fig, ax = plt.subplots()
    ax.bar([i - width / 2 for i in x], bt_times, width, label="backtracking")
    ax.bar([i + width / 2 for i in x], sa_times, width, label="recocido simulado")
    ax.set_xticks(list(x))
    ax.set_xticklabels([f"N={n}" for n in sizes])
    ax.set_ylabel("tiempo (s)")
    ax.set_title("N-reinas: tiempo por metodo")
    ax.legend()
    _save(fig, "nqueens_time.png")


def plot_graph_coloring_time() -> None:
    rows = _read_csv(results_path("tables", "graph_coloring.csv"))
    if not rows:
        return

    sizes = sorted({int(r["instance_size"]) for r in rows})
    bt_times = [
        next(
            (
                float(r["time_seconds"])
                for r in rows
                if int(r["instance_size"]) == n
                and r["method"].startswith("backtracking")
            ),
            None,
        )
        for n in sizes
    ]
    sa_times = [
        next(
            (
                float(r["time_seconds"])
                for r in rows
                if int(r["instance_size"]) == n and r["method"] == "simulated_annealing"
            ),
            None,
        )
        for n in sizes
    ]

    x = range(len(sizes))
    width = 0.35
    fig, ax = plt.subplots()
    ax.bar([i - width / 2 for i in x], bt_times, width, label="backtracking")
    ax.bar([i + width / 2 for i in x], sa_times, width, label="recocido simulado")
    ax.set_xticks(list(x))
    ax.set_xticklabels([f"{n} nodos" for n in sizes])
    ax.set_ylabel("tiempo (s)")
    ax.set_title("Coloreado de grafos: tiempo por metodo")
    ax.legend()
    _save(fig, "graph_coloring_time.png")


def plot_coloring_comparison() -> None:
    rows = _read_csv(results_path("tables", "coloring_comparison.csv"))
    if not rows:
        return

    instances = [r["instance"] for r in rows]
    methods = ["backtracking", "metaheuristic", "ortools"]
    labels = ["backtracking", "recocido simulado", "OR-Tools"]

    for metric, ylabel, fname in [
        ("k", "colores usados (k)", "coloring_comparison_k.png"),
        ("time", "tiempo (s)", "coloring_comparison_time.png"),
    ]:
        x = range(len(instances))
        width = 0.25
        fig, ax = plt.subplots()
        for i, (method, label) in enumerate(zip(methods, labels)):
            values = [
                float(r[f"{metric}_{method}"])
                if r[f"{metric}_{method}"] not in ("", "None")
                else None
                for r in rows
            ]
            offset = (i - 1) * width
            ax.bar([xi + offset for xi in x], values, width, label=label)
        ax.set_xticks(list(x))
        ax.set_xticklabels(instances)
        ax.set_ylabel(ylabel)
        ax.set_title(f"Coloreado de grafos vs. OR-Tools: {ylabel}")
        ax.legend()
        _save(fig, fname)


def plot_sa_convergence() -> None:
    targets = [
        (
            "nqueens_8_metaheuristic.json",
            "N-reinas N=8: convergencia del recocido simulado",
        ),
        (
            "nqueens_100_metaheuristic.json",
            "N-reinas N=100: convergencia del recocido simulado",
        ),
        (
            "coloring_small_metaheuristic.json",
            "Coloreado 50 nodos: convergencia del recocido simulado",
        ),
        (
            "coloring_large_metaheuristic.json",
            "Coloreado 1000 nodos: convergencia del recocido simulado",
        ),
    ]
    for filename, title in targets:
        data = _read_json(results_path("solutions", filename))
        if data is None:
            continue
        energy = data["stats"]["extra"].get("energy_history")
        if not energy:
            continue

        fig, ax = plt.subplots()
        ax.plot(energy, linewidth=0.8)
        ax.set_xlabel("iteracion")
        ax.set_ylabel("conflictos (energia)")
        ax.set_title(title)
        _save(fig, filename.replace(".json", "_convergence.png"))


def main() -> None:
    plot_nqueens_time()
    plot_graph_coloring_time()
    plot_coloring_comparison()
    plot_sa_convergence()


if __name__ == "__main__":
    main()
