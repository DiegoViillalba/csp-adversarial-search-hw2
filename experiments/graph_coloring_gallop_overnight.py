"""Overnight GALLOPING search for gc_1000_9's chromatic number, replacing
naive bisection (graph_coloring_bisect_overnight.py): that script's very
first probe picked the blind midpoint of [48, 310] (k=179), which turned
out UNKNOWN even after 1200s -> 2400s of retry -- 3600s spent and the
window didn't move AT ALL. The problem with plain bisection is that it
assumes only a narrow region near the true boundary is hard and everywhere
else is easy; at this scale (1000 vertices, ~450K edges) that assumption
doesn't hold -- there's apparently a WIDE region of difficulty, not a
narrow spike, so a blind midpoint guess can land somewhere expensive
without telling you anything useful.

Galloping search instead starts from a point ALREADY PROVEN easy (k=310,
confirmed feasible in ~450s or less by graph_coloring_boundary_overnight.py)
and steps DOWNWARD with a step size that:
  - DOUBLES after a fast, clean OPTIMAL (still comfortably in easy
    territory, so probe more aggressively)
  - HALVES after anything that ISN'T a fast OPTIMAL (INFEASIBLE or
    UNKNOWN) -- that candidate was too aggressive a jump, so back off and
    probe closer to the last known-good point instead

This is the same idea as exponential/galloping search used elsewhere (git
bisect's early steps, TCP slow-start, interpolation search): explore the
"free" direction fast, and only spend real budget once you're actually
near where it gets hard. It naturally degrades into something bisection-
like once the step shrinks to 1, but arrives there having spent almost
nothing on the parts of the range that turned out to be easy.

Coloring is still monotonic in k, so a PROVEN infeasible candidate tightens
`lo` and a PROVEN feasible one tightens `hi`, exactly like the bisection
script -- the only thing that changed is HOW the next candidate is chosen,
not the correctness argument for narrowing the window.

Reuses solve_with_retry from graph_coloring_bisect_overnight.py (same
retry-once-at-double-budget-on-UNKNOWN logic) rather than duplicating it.

Writes to results/tables/graph_coloring_gallop_overnight.csv, separate from
both the bisect script's and the linear sweep's CSVs.
"""

from __future__ import annotations

import time

from _common import load_config, results_path
from graph_coloring_bisect_overnight import solve_with_retry
from run_graph_coloring import ensure_instance

from src.utils.graph_io import write_coloring
from src.utils.metrics import SearchStats, append_result_csv, save_solution_json
from src.utils.validation import is_valid_coloring

INSTANCE_NAME = "large"
LO = 48  # PROBADO infactible (clique de tamano 49)
HI = 310  # PROBADO factible y RAPIDO (graph_coloring_boundary_overnight.py, ~450s o menos)
INITIAL_STEP = 8  # primer salto hacia abajo desde HI
INITIAL_TIME_LIMIT_SECONDS = 15 * 60  # 15 min por intento base -- se resetea tras un exito rapido
MAX_TIME_LIMIT_SECONDS = 2 * 3600  # tope tras reintentos repetidos en la misma zona dura
OVERALL_BUDGET_SECONDS = 10 * 3600


def main() -> None:
    config = load_config("graph_coloring")
    instance = next(i for i in config["instances"] if i["name"] == INSTANCE_NAME)
    num_vertices, edges = ensure_instance(instance, config["seed"])

    csv_path = results_path("tables", "graph_coloring_gallop_overnight.csv")
    start = time.perf_counter()
    lo, hi = LO, HI
    step = INITIAL_STEP
    time_limit = INITIAL_TIME_LIMIT_SECONDS
    best_feasible_coloring = None
    best_feasible_stats = None

    print(f"ventana inicial: [{lo}, {hi}], paso inicial={step}", flush=True)

    while hi - lo > 1:
        if time.perf_counter() - start > OVERALL_BUDGET_SECONDS:
            print(f"\npresupuesto total agotado -- ventana final: [{lo}, {hi}]", flush=True)
            break

        candidate = max(lo + 1, hi - step)
        print(
            f"\n=== ventana [{lo}, {hi}] paso={step} -> probando k={candidate} "
            f"(time_limit={time_limit:.0f}s) ===",
            flush=True,
        )

        coloring, stats, time_limit_used = solve_with_retry(
            num_vertices, edges, candidate, time_limit
        )

        row = SearchStats(
            method="ortools_gallop",
            problem="graph_coloring",
            instance_size=num_vertices,
            solved=stats["status"] == "OPTIMAL",
            time_seconds=stats["time_seconds"],
            extra={
                "k": candidate,
                "status": stats["status"],
                "step": step,
                "window_lo_before": lo,
                "window_hi_before": hi,
            },
        )
        append_result_csv(csv_path, row)
        print(
            f"  k={candidate}: status={stats['status']} time={stats['time_seconds']:.1f}s",
            flush=True,
        )

        if stats["status"] == "OPTIMAL":
            hi = candidate
            best_feasible_coloring = coloring
            best_feasible_stats = row
            step *= 2  # seguimos en zona facil, galopar mas rapido
            time_limit = INITIAL_TIME_LIMIT_SECONDS  # fue facil, no hace falta mas presupuesto
            print(f"  facil y rapido -> hi={hi}, paso ahora {step}", flush=True)
        elif stats["status"] == "INFEASIBLE":
            lo = candidate
            step = max(1, step // 2)
            time_limit = INITIAL_TIME_LIMIT_SECONDS
            print(f"  PROBADO infactible -> lo={lo}, retrocedo el paso a {step}", flush=True)
        else:  # UNKNOWN incluso tras reintentar en solve_with_retry
            if step == 1:
                print(
                    f"\nk={candidate} sigue indeciso incluso con paso minimo -- me detengo aqui",
                    flush=True,
                )
                break
            step = max(1, step // 2)
            print(f"  indeciso -> retrocedo el paso a {step}, mismo lo/hi", flush=True)

        elapsed = time.perf_counter() - start
        print(
            f"  ventana ahora: [{lo}, {hi}]  presupuesto usado: {elapsed:.1f}s / {OVERALL_BUDGET_SECONDS}s",
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
            results_path("solutions", f"coloring_{INSTANCE_NAME}_gallop_overnight.json"),
            best_feasible_coloring,
            best_feasible_stats,
        )
        write_coloring(
            results_path("solutions", f"coloring_{INSTANCE_NAME}_gallop_overnight.txt"),
            best_feasible_coloring,
        )


if __name__ == "__main__":
    main()
