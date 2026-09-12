"""Attempts to enumerate ALL N-queens solutions for N in
configs/nqueens.yaml (enumerate_all.n), bounded by max_solutions and/or
time_limit_seconds. See README.md for why exhaustively enumerating at N=100
is not actually attempted, and what to report instead.

Expects src/problems/nqueens.py to expose:
    enumerate_solutions(n, max_solutions, time_limit_seconds)
        -> (list[list[int]], SearchStats)
    where stats.extra["exhaustive"] is True iff the search finished on its
    own (not cut off by max_solutions/time_limit_seconds).
"""
from __future__ import annotations

from _common import load_config, results_path

from src.problems import nqueens
from src.utils.metrics import append_result_csv, save_solution_json
from src.utils.validation import is_valid_nqueens_solution


def main() -> None:
    config = load_config("nqueens")["enumerate_all"]

    solutions, stats = nqueens.enumerate_solutions(
        n=config["n"],
        max_solutions=config["max_solutions"],
        time_limit_seconds=config["time_limit_seconds"],
    )

    assert all(is_valid_nqueens_solution(s) for s in solutions), "an enumerated solution is invalid"

    append_result_csv(results_path("tables", "nqueens_enumeration.csv"), stats)
    save_solution_json(
        results_path("solutions", f"nqueens_{config['n']}_all_solutions.json"), solutions, stats
    )

    print(
        f"n={config['n']}: found {len(solutions)} solutions in {stats.time_seconds:.2f}s "
        f"(exhaustive={stats.extra.get('exhaustive')})"
    )


if __name__ == "__main__":
    main()
