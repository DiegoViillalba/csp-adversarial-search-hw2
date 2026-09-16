"""Overnight boundary probe, going DOWNWARD instead of up: the regular sweep
(run_graph_coloring.py, 120s/k, k=10..70) found gc_50_7 feasible at k=14, but
k=10..13 all just timed out -- ambiguous, could be genuinely infeasible or
could just need more time than 120s (classic easy-hard-easy phase transition
right at the satisfiability boundary, see Cheeseman/Kanefsky/Taylor 1991 --
worth citing in the report). Exploratory, not one of the assignment's
required deliverables.

Also used for gc_1000_9, where the regular sweep (k=10..70) never even
reaches feasibility -- for that instance K_START_BELOW isn't a k the
ascending sweep confirmed, it's a greedy-coloring upper bound (315 colors,
networkx largest_first strategy on this graph -- a real, constructive proof
that k=315 works, just not necessarily the smallest k that does). Either
way the property this script relies on is the same: SOME k below the
starting point is known/provably feasible, and we're hunting for the
smallest one.

Starts one below the known-feasible K_START_BELOW and works down, giving
each k a real budget across THREE independent methods instead of the
regular pipeline's 120s cap on just two:
  1. OR-Tools (CP-SAT)  -- by far the best at PROVING infeasibility, not
     just timing out: solve_coloring_ortools's status is INFEASIBLE (proof)
     vs UNKNOWN (ran out of time, undecided). Tried first for that reason.
  2. backtracking+FC+AC3 -- can also prove infeasibility (exhausts the tree),
     just slower than CP-SAT's learned clause propagation.
  3. simulated annealing -- can't prove infeasibility (it's incomplete), but
     may stumble onto a feasible coloring faster than the other two finish.

Coloring is monotonic in k (feasible at k' implies feasible at every k>k'),
so PROVEN-infeasible at k implies infeasible at every k<k too -- the moment
OR-Tools or backtracking actually proves one k infeasible (not just times
out), everything below it is automatically decided and the sweep stops.
That monotonicity is the only real shortcut available; there's no way
around at least one method needing a real budget to either find a solution
or exhaust the search tree for whichever k turns out to be the true
boundary.

PER_METHOD_TIME_LIMIT_SECONDS / OVERALL_BUDGET_SECONDS are hardcoded here
rather than read from configs/graph_coloring.yaml on purpose, same
rationale as the other *_overnight.py scripts: that config is shared with
the regular, fast pipeline, and bumping it there would make every normal
run take hours too.

Writes to *_boundary_overnight.csv/.json filenames so this never collides
with results/tables/graph_coloring.csv or graph_coloring_k_sweep.csv from
the regular run.
"""

from __future__ import annotations

import time

from _common import load_config, results_path
from run_graph_coloring import ensure_instance

from src.integrations.ortools_coloring import solve_coloring_ortools
from src.problems import graph_coloring
from src.utils.metrics import append_result_csv, save_solution_json
from src.utils.validation import is_valid_coloring

# Para gc_50_7 (probado, ver conversacion): INSTANCE_NAME = "small", K_START_BELOW = 14
# (14 confirmado factible por el sweep ascendente normal).
INSTANCE_NAME = "large"  # "small" o "large" -- que instancia de configs/graph_coloring.yaml
K_START_BELOW = 315  # cota superior real: coloreo voraz (networkx largest_first) en gc_1000_9
FLOOR_K = 2  # no seguir bajando de aqui aunque quede presupuesto
PER_METHOD_TIME_LIMIT_SECONDS = 20 * 60  # 20 min por metodo, por k
OVERALL_BUDGET_SECONDS = 8 * 3600  # techo total del script, sin importar en que k vaya
SEED = 42


def main() -> None:
    config = load_config("graph_coloring")
    instance = next(i for i in config["instances"] if i["name"] == INSTANCE_NAME)
    num_vertices, edges = ensure_instance(instance, config["seed"])

    csv_path = results_path("tables", "graph_coloring_boundary_overnight.csv")
    start = time.perf_counter()
    smallest_feasible_k = None
    smallest_feasible_coloring = None

    for k in range(K_START_BELOW - 1, FLOOR_K - 1, -1):
        if time.perf_counter() - start > OVERALL_BUDGET_SECONDS:
            print(f"presupuesto total agotado, me detengo antes de probar k={k}")
            break

        print(f"\n=== k={k} ===", flush=True)

        # 1. OR-Tools primero: el mas capaz de PROBAR infactibilidad en vez
        # de solo agotar el tiempo sin concluir nada.
        coloring_or, stats_or = solve_coloring_ortools(
            num_vertices, edges, k, PER_METHOD_TIME_LIMIT_SECONDS
        )
        print(
            f"  ortools: status={stats_or['status']} time={stats_or['time_seconds']:.1f}s",
            flush=True,
        )
        if stats_or["status"] == "INFEASIBLE":
            print(
                f"k={k} PROBADO infactible por OR-Tools -- por monotonia, "
                f"k<{k} tambien lo son. Me detengo aqui."
            )
            break

        # 2. backtracking+FC+AC3: tambien puede probar infactibilidad,
        # solo que mas lento que CP-SAT.
        coloring_bt, stats_bt = graph_coloring.solve_backtracking(
            num_vertices,
            edges,
            k,
            use_forward_checking=True,
            use_ac3=True,
            time_limit_seconds=PER_METHOD_TIME_LIMIT_SECONDS,
        )
        append_result_csv(csv_path, stats_bt)
        print(
            f"  backtracking: solved={coloring_bt is not None} "
            f"timed_out={stats_bt.extra.get('timed_out')} "
            f"time={stats_bt.time_seconds:.1f}s",
            flush=True,
        )
        if coloring_bt is None and not stats_bt.extra.get("timed_out"):
            print(
                f"k={k} PROBADO infactible por backtracking -- por monotonia, "
                f"k<{k} tambien lo son. Me detengo aqui."
            )
            break

        # 3. Metaheuristica: no prueba infactibilidad, pero puede encontrar
        # una coloracion valida mas rapido que las dos de arriba.
        coloring_sa, stats_sa = graph_coloring.solve_metaheuristic(
            num_vertices,
            edges,
            k,
            seed=SEED,
            initial_temperature=10.0,
            cooling_rate=0.995,
            max_iterations=10_000_000,
            time_limit_seconds=PER_METHOD_TIME_LIMIT_SECONDS,
        )
        conflicts_sa = graph_coloring.count_conflicts(edges, coloring_sa)
        append_result_csv(csv_path, stats_sa)
        print(
            f"  metaheuristic: conflictos={conflicts_sa} time={stats_sa.time_seconds:.1f}s",
            flush=True,
        )

        feasible_coloring = None
        if coloring_or is not None:
            feasible_coloring = coloring_or
        elif coloring_bt is not None:
            feasible_coloring = coloring_bt
        elif conflicts_sa == 0:
            feasible_coloring = coloring_sa

        if feasible_coloring is not None:
            assert is_valid_coloring(edges, feasible_coloring)
            smallest_feasible_k = k
            smallest_feasible_coloring = feasible_coloring
            save_solution_json(
                results_path(
                    "solutions",
                    f"coloring_{INSTANCE_NAME}_boundary_k{k}_overnight.json",
                ),
                feasible_coloring,
                stats_bt,
            )
            print(f"  k={k}: FACTIBLE (algun metodo lo resolvio)")
        else:
            print(f"  k={k}: ningun metodo concluyo nada (los 3 se quedaron sin decidir)")

        elapsed_total = time.perf_counter() - start
        print(f"  presupuesto usado hasta ahora: {elapsed_total:.1f}s / {OVERALL_BUDGET_SECONDS}s")

    print(f"\nresumen: menor k factible encontrado en este run = {smallest_feasible_k}")
    if smallest_feasible_coloring is not None:
        write_path = results_path(
            "solutions", f"coloring_{INSTANCE_NAME}_boundary_overnight.txt"
        )
        from src.utils.graph_io import write_coloring

        write_coloring(write_path, smallest_feasible_coloring)


if __name__ == "__main__":
    main()
