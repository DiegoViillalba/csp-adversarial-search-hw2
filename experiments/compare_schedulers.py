"""Compares the three SA cooling schedules (geometric, exponential,
sinusoidal) on time-to-converge and solution quality: how much does the
schedule actually affect convergence? Not one of the assignment's required
deliverables -- exploratory, for the report's discussion of design choices
in the recocido simulado.

Each scheduler needs `cooling_rate` in a different order of magnitude (see
the docstrings in src/metaheuristics/simulated_annealing.py): geometric is
a per-step multiplier close to 1, exponential/sinusoidal are decay rates
two orders of magnitude smaller. SCHEDULERS below pairs each schedule with
a rate that actually cools over the run instead of freezing (geometric
with a tiny rate) or decaying to ~0 almost immediately (exponential/
sinusoidal with a rate close to 1).

Runs on the same N=100 queens instance and the same 1000-node coloring
instance (at k=9, the value run_graph_coloring.py already found feasible
for it) used elsewhere in this project, a few seeds each for a less noisy
time estimate. Writes results/tables/scheduler_comparison.csv and one
energy_history per (instance, scheduler) into results/solutions/ for
make_plots.py to overlay as convergence curves.
"""

from __future__ import annotations

import csv

from _common import load_config, results_path
from run_graph_coloring import ensure_instance

from src.metaheuristics.simulated_annealing import (
    exponential_schedule,
    geometric_schedule,
    simulated_annealing,
    sinusoidal_schedule,
)
from src.problems.graph_coloring import build_graph_coloring_csp
from src.problems.nqueens import build_nqueens_csp
from src.utils.metrics import SearchStats, save_solution_json, timer

SCHEDULERS = [
    ("geometric", geometric_schedule, 0.995),
    ("exponential", exponential_schedule, 0.005),
    ("sinusoidal", sinusoidal_schedule, 0.005),
]

SEEDS = [1, 2, 3]


def run_instance(
    problem_name: str,
    problem,
    instance_size: int,
    max_iterations: int,
    time_limit_seconds: float,
) -> list[dict]:
    rows = []
    for scheduler_name, scheduler_fn, cooling_rate in SCHEDULERS:
        for seed in SEEDS:
            with timer() as elapsed:
                best, best_cost, energy = simulated_annealing(
                    problem,
                    initial_temperature=10.0,
                    cooling_rate=cooling_rate,
                    max_iterations=max_iterations,
                    time_limit_seconds=time_limit_seconds,
                    seed=seed,
                    scheduler=scheduler_fn,
                )
            rows.append(
                {
                    "problem": problem_name,
                    "instance_size": instance_size,
                    "scheduler": scheduler_name,
                    "seed": seed,
                    "cooling_rate": cooling_rate,
                    "final_conflicts": best_cost,
                    "solved": best_cost == 0,
                    "time_seconds": elapsed(),
                    "iterations": len(energy) - 1,
                }
            )
            # Only the first seed's energy_history is kept per scheduler for
            # the convergence plot -- overlaying all seeds would be noise.
            if seed == SEEDS[0]:
                save_solution_json(
                    results_path(
                        "solutions",
                        f"schedulers_{problem_name}_{scheduler_name}.json",
                    ),
                    best,
                    SearchStats(
                        method=f"simulated_annealing+{scheduler_name}",
                        problem=problem_name,
                        instance_size=instance_size,
                        solved=best_cost == 0,
                        objective=best_cost,
                        time_seconds=elapsed(),
                        extra={"energy_history": energy, "cooling_rate": cooling_rate},
                    ),
                )
            print(rows[-1])
    return rows


def main() -> None:
    rows = []

    nqueens_config = load_config("nqueens")
    problem = build_nqueens_csp(100)
    rows += run_instance(
        "nqueens",
        problem,
        100,
        max_iterations=nqueens_config["metaheuristic"]["max_iterations"],
        time_limit_seconds=nqueens_config["metaheuristic"]["time_limit_seconds"],
    )

    coloring_config = load_config("graph_coloring")
    large = coloring_config["instances"][1]
    num_vertices, edges = ensure_instance(large, coloring_config["seed"])
    problem = build_graph_coloring_csp(num_vertices, edges, k=9)
    rows += run_instance(
        "graph_coloring",
        problem,
        num_vertices,
        max_iterations=coloring_config["metaheuristic"]["max_iterations"],
        time_limit_seconds=coloring_config["metaheuristic"]["time_limit_seconds"],
    )

    path = results_path("tables", "scheduler_comparison.csv")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
