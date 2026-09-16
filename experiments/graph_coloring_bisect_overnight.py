"""Overnight BINARY SEARCH for gc_1000_9's chromatic number, replacing the
linear downward sweep in graph_coloring_boundary_overnight.py: that script
found k=310..314 all feasible in ~7000s each (OR-Tools' own solve time kept
growing 156s->450s as k dropped), and backtracking/the metaheuristic never
resolved a single k at this scale within 20 min each -- neither contributed
any signal, just burned budget. Exploratory, not one of the assignment's
required deliverables.

Coloring is monotonic in k (feasible at k' implies feasible at every k>k';
infeasible at k implies infeasible at every k<k), so instead of testing
every k in a range, this bisects it: ~9 OR-Tools calls to close [LO, HI]
down to a single point instead of up to (HI-LO) linear steps. Only
OR-Tools is used here -- it's the only one of the three methods that
actually decided anything at this scale last run.

Starting window is [LO, HI], both already PROVEN, not guessed:
  LO = 48   -- infeasible: a 49-vertex clique (networkx's approximate
              max_clique on this graph) needs 49 distinct colors, so k=48
              (and everything below) cannot work.
  HI = 310  -- feasible: OR-Tools found an actual valid coloring at k=310
              in graph_coloring_boundary_overnight.py's last run (tighter
              than the greedy bound of 315 this exploration started from).

Each bisect step tries mid = (lo+hi)//2 with OR-Tools:
  OPTIMAL     -> mid is feasible,   hi = mid    (new window: [lo, mid])
  INFEASIBLE  -> mid is infeasible, lo = mid+1  (new window: [mid+1, hi])
  UNKNOWN     -> ran out of time, undecided. Retried once at double the
                 time budget (see solve_with_retry); if STILL UNKNOWN, the
                 window can't be narrowed past this point and the run
                 stops there. That's a legitimate, reportable result on its
                 own -- a narrower bracket than [48, 310], even if not a
                 single exact number -- same honesty-over-completeness
                 convention the README already uses for N=100 queens
                 enumeration under "Explorar limites de computo".

The per-attempt time budget starts at INITIAL_TIME_LIMIT_SECONDS and only
grows when a call comes back UNKNOWN (doubling, capped at
MAX_TIME_LIMIT_SECONDS) -- steps near the true boundary tend to be the hard
ones, and they cluster near the end of a bisection, so this naturally
spends more time exactly where it's needed instead of upfront.

Writes EVERY attempt (not just the decisive ones) to
results/tables/graph_coloring_bisect_overnight.csv, and prints one line per
attempt showing the CURRENT window before and after -- so `tail -f` shows
the window actually closing in over time, not just isolated per-k outcomes.
"""

from __future__ import annotations

import time

from _common import load_config, results_path
from run_graph_coloring import ensure_instance

from src.integrations.ortools_coloring import solve_coloring_ortools
from src.utils.graph_io import write_coloring
from src.utils.metrics import SearchStats, append_result_csv, save_solution_json
from src.utils.validation import is_valid_coloring

INSTANCE_NAME = "large"
LO = 48  # PROBADO infactible (clique de tamano 49, ver conversacion)
HI = 310  # PROBADO factible (OR-Tools, corrida de graph_coloring_boundary_overnight.py)
INITIAL_TIME_LIMIT_SECONDS = 20 * 60  # 20 min, igual que el sweep lineal anterior
MAX_TIME_LIMIT_SECONDS = 3 * 3600  # tope por intento individual, incluso tras reintentar
OVERALL_BUDGET_SECONDS = 10 * 3600  # techo total del script, sin importar en que k vaya


def solve_with_retry(num_vertices, edges, k, time_limit):
    """Intenta k con time_limit; si el resultado es UNKNOWN (ni probo
    factible ni infactible), duplica el presupuesto y reintenta UNA vez mas
    (tope MAX_TIME_LIMIT_SECONDS). Regresa (coloring, stats, time_limit
    usado en el ultimo intento) -- ese time_limit se reutiliza como punto
    de partida del siguiente k, porque estar cerca de la frontera real
    tiende a seguir siendo dificil, no es un evento aislado."""
    coloring, stats = solve_coloring_ortools(num_vertices, edges, k, time_limit)
    if stats["status"] != "UNKNOWN":
        return coloring, stats, time_limit

    retry_limit = min(time_limit * 2, MAX_TIME_LIMIT_SECONDS)
    if retry_limit <= time_limit:
        return coloring, stats, time_limit  # ya estabamos en el tope, no vale la pena reintentar

    print(
        f"    k={k} indeciso en {time_limit:.0f}s, reintentando con {retry_limit:.0f}s",
        flush=True,
    )
    coloring, stats = solve_coloring_ortools(num_vertices, edges, k, retry_limit)
    return coloring, stats, retry_limit


def main() -> None:
    config = load_config("graph_coloring")
    instance = next(i for i in config["instances"] if i["name"] == INSTANCE_NAME)
    num_vertices, edges = ensure_instance(instance, config["seed"])

    csv_path = results_path("tables", "graph_coloring_bisect_overnight.csv")
    start = time.perf_counter()
    lo, hi = LO, HI
    time_limit = INITIAL_TIME_LIMIT_SECONDS
    best_feasible_coloring = None
    best_feasible_stats = None

    print(
        f"ventana inicial: [{lo}, {hi}] "
        f"({lo} probado infactible, {hi} probado factible)",
        flush=True,
    )

    while hi - lo > 1:
        if time.perf_counter() - start > OVERALL_BUDGET_SECONDS:
            print(
                f"\npresupuesto total agotado -- ventana final sin cerrar: [{lo}, {hi}]",
                flush=True,
            )
            break

        mid = (lo + hi) // 2
        print(f"\n=== ventana [{lo}, {hi}] -> probando k={mid} ===", flush=True)

        coloring, stats, time_limit = solve_with_retry(num_vertices, edges, mid, time_limit)

        row = SearchStats(
            method="ortools_bisect",
            problem="graph_coloring",
            instance_size=num_vertices,
            solved=stats["status"] == "OPTIMAL",
            time_seconds=stats["time_seconds"],
            extra={
                "k": mid,
                "status": stats["status"],
                "window_lo_before": lo,
                "window_hi_before": hi,
            },
        )
        append_result_csv(csv_path, row)
        print(f"  k={mid}: status={stats['status']} time={stats['time_seconds']:.1f}s", flush=True)

        if stats["status"] == "OPTIMAL":
            hi = mid
            best_feasible_coloring = coloring
            best_feasible_stats = row
        elif stats["status"] == "INFEASIBLE":
            lo = mid + 1
        else:  # UNKNOWN incluso tras reintentar en solve_with_retry
            print(
                f"  k={mid} sigue indeciso -- no puedo cerrar mas la ventana desde aqui, me detengo",
                flush=True,
            )
            break

        elapsed = time.perf_counter() - start
        print(
            f"  ventana ahora: [{lo}, {hi}]  "
            f"presupuesto usado: {elapsed:.1f}s / {OVERALL_BUDGET_SECONDS}s",
            flush=True,
        )

    print(f"\nresumen: ventana final = [{lo}, {hi}]", flush=True)
    if hi - lo <= 1:
        print(f"numero cromatico determinado exactamente: {hi}", flush=True)
    else:
        print(f"no se cerro del todo -- el numero cromatico real esta en [{lo}, {hi}]", flush=True)

    if best_feasible_coloring is not None:
        assert is_valid_coloring(edges, best_feasible_coloring)
        save_solution_json(
            results_path("solutions", f"coloring_{INSTANCE_NAME}_bisect_overnight.json"),
            best_feasible_coloring,
            best_feasible_stats,
        )
        write_coloring(
            results_path("solutions", f"coloring_{INSTANCE_NAME}_bisect_overnight.txt"),
            best_feasible_coloring,
        )


if __name__ == "__main__":
    main()
