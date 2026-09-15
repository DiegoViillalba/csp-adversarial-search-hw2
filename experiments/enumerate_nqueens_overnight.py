"""Overnight, much-larger-budget run of nqueens.enumerate_solutions for
N=100: the regular enumerate_nqueens.py (configs/nqueens.yaml, capped at
300s) reliably finds 0 solutions in that time -- this removes that
practical ceiling to see how far a real compute budget actually gets.
Exploratory, not one of the assignment's required deliverables.

TIME_LIMIT_SECONDS is hardcoded here rather than read from
configs/nqueens.yaml on purpose: that config is shared with the regular,
fast pipeline (run_nqueens.py / scripts/run_remote_heavy.sh), and bumping
it there would make every normal run take 5 hours too.

Writes to *_overnight.csv/.json filenames so this never collides with or
overwrites results/tables/nqueens_enumeration.csv from the regular run.
"""

from __future__ import annotations

from _common import results_path

from src.problems import nqueens
from src.utils.metrics import append_result_csv, save_solution_json
from src.utils.validation import is_valid_nqueens_solution

N = 100
TIME_LIMIT_SECONDS = 5 * 3600  # 5 horas
MAX_SOLUTIONS = None  # sin tope de cantidad -- solo el de tiempo


def main() -> None:
    solutions, stats = nqueens.enumerate_solutions(
        n=N, max_solutions=MAX_SOLUTIONS, time_limit_seconds=TIME_LIMIT_SECONDS
    )
    assert all(is_valid_nqueens_solution(s) for s in solutions), (
        "an enumerated solution is invalid"
    )

    append_result_csv(
        results_path("tables", "nqueens_enumeration_overnight.csv"), stats
    )
    save_solution_json(
        results_path("solutions", f"nqueens_{N}_all_solutions_overnight.json"),
        solutions,
        stats,
    )
    print(
        f"n={N}: found {len(solutions)} solutions in {stats.time_seconds:.2f}s "
        f"(exhaustive={stats.extra.get('exhaustive')})"
    )


if __name__ == "__main__":
    main()
