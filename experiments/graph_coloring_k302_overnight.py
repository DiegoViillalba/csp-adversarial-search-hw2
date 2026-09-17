"""Overnight comparison AT k=302 -- the smallest k confirmed feasible so far
for gc_1000_9.txt (OR-Tools, OPTIMAL in ~858s, see
graph_coloring_gallop_overnight.py's last run) -- between:

  1. backtracking+FC+MRV+LCV, with AC3 on vs. off
  2. simulated annealing with each of the three cooling schedules
     (geometric / exponential / sinusoidal), tracking energy_history for a
     convergence plot

K=302 is FIXED here on purpose, not searched for: we already know (proven
by a complete solver) that a valid coloring exists at that k. The question
this answers is different from graph_coloring_gallop_overnight.py's --
not "what's the smallest feasible k", but "how do OUR OWN two methods
behave at a k we already know has a solution", which is what the
assignment's "comparar tiempo de computo y calidad" actually asks for.

This repeats what graph_coloring_boundary_overnight.py already showed at
k=310-314 (backtracking times out, SA doesn't converge), now at the exact
k OR-Tools settled on, plus the scheduler breakdown that
experiments/compare_schedulers.py never got right for this instance --
that script still hardcodes k=9 (the OLD synthetic graph's answer, before
gc_1000_9.txt replaced it) and a 120s budget, both far too small at this
scale.

Writes results/tables/graph_coloring_k302_overnight.csv, and one
energy_history JSON per scheduler into results/solutions/ for
make_plots.py-style convergence plots.
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
from src.problems import graph_coloring
from src.problems.graph_coloring import build_graph_coloring_csp
from src.utils.metrics import SearchStats, save_solution_json, timer
from src.utils.validation import is_valid_coloring

INSTANCE_NAME = "large"
K = 302  # ya confirmado factible por OR-Tools (graph_coloring_gallop_overnight.py)
BACKTRACKING_TIME_LIMIT_SECONDS = 30 * 60
SA_TIME_LIMIT_SECONDS = 30 * 60
SA_MAX_ITERATIONS = 10_000_000
SEED = 42
SCHEDULERS = [
    ("geometric", geometric_schedule, 0.995),
    ("exponential", exponential_schedule, 0.005),
    ("sinusoidal", sinusoidal_schedule, 0.005),
]


def main() -> None:
    config = load_config("graph_coloring")
    instance = next(i for i in config["instances"] if i["name"] == INSTANCE_NAME)
    num_vertices, edges = ensure_instance(instance, config["seed"])

    rows: list[dict] = []

    # 1. Backtracking con y sin AC3 (ambos con FC + MRV + LCV)
    print(f"=== backtracking en k={K} (n={num_vertices}, {len(edges)} aristas) ===", flush=True)
    for use_ac3 in (True, False):
        label = "fc+ac3" if use_ac3 else "fc_sin_ac3"
        print(f"  {label}...", flush=True)
        coloring, stats = graph_coloring.solve_backtracking(
            num_vertices,
            edges,
            K,
            use_forward_checking=True,
            use_ac3=use_ac3,
            time_limit_seconds=BACKTRACKING_TIME_LIMIT_SECONDS,
        )
        if coloring is not None:
            assert is_valid_coloring(edges, coloring)
        rows.append(
            {
                "method": f"backtracking+{label}",
                "k": K,
                "solved": coloring is not None,
                "nodes_expanded": stats.nodes_expanded,
                "time_seconds": stats.time_seconds,
                "timed_out": stats.extra.get("timed_out"),
            }
        )
        print(
            f"    solved={coloring is not None} nodes={stats.nodes_expanded} "
            f"time={stats.time_seconds:.1f}s timed_out={stats.extra.get('timed_out')}",
            flush=True,
        )

    # 2. Recocido simulado, cada scheduler, con energy_history para graficar
    print(f"\n=== metaheuristica en k={K}, 3 schedulers ===", flush=True)
    problem = build_graph_coloring_csp(num_vertices, edges, k=K)
    for name, scheduler_fn, cooling_rate in SCHEDULERS:
        print(f"  {name}...", flush=True)
        with timer() as elapsed:
            best, best_cost, energy = simulated_annealing(
                problem,
                initial_temperature=10.0,
                cooling_rate=cooling_rate,
                max_iterations=SA_MAX_ITERATIONS,
                time_limit_seconds=SA_TIME_LIMIT_SECONDS,
                seed=SEED,
                scheduler=scheduler_fn,
            )
        rows.append(
            {
                "method": f"simulated_annealing+{name}",
                "k": K,
                "solved": best_cost == 0,
                "final_conflicts": best_cost,
                "time_seconds": elapsed(),
                "iterations": len(energy) - 1,
            }
        )
        save_solution_json(
            results_path("solutions", f"graph_coloring_k302_{name}.json"),
            best,
            SearchStats(
                method=f"simulated_annealing+{name}",
                problem="graph_coloring",
                instance_size=num_vertices,
                solved=best_cost == 0,
                objective=best_cost,
                time_seconds=elapsed(),
                extra={"energy_history": energy, "cooling_rate": cooling_rate, "k": K},
            ),
        )
        print(
            f"    conflictos={best_cost} tiempo={elapsed():.1f}s iteraciones={len(energy) - 1}",
            flush=True,
        )

    path = results_path("tables", "graph_coloring_k302_overnight.csv")
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, restval="")
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nescrito: {path}")


if __name__ == "__main__":
    main()
