"""Runs N-queens with backtracking and with the metaheuristic, for every N in
configs/nqueens.yaml, and logs comparable stats to results/.

Expects src/problems/nqueens.py to expose:
    solve_backtracking(n, use_forward_checking, use_ac3, time_limit_seconds)
        -> (positions | None, SearchStats)
    solve_metaheuristic(n, seed, **params) -> (positions, SearchStats)
    count_conflicts(positions) -> int
See README.md ("Interfaces esperadas") for the full contract.
"""

from __future__ import annotations

from _common import load_config, results_path

from src.problems import nqueens
from src.utils.metrics import append_result_csv, save_solution_json
from src.utils.random_seed import set_seed
from src.utils.validation import is_valid_nqueens_solution


def main() -> None:
    config = load_config("nqueens")
    set_seed(config["seed"])
    csv_path = results_path("tables", "nqueens.csv")

    for n in config["sizes"]:
        positions_bt, stats_bt = nqueens.solve_backtracking(
            n,
            use_forward_checking=config["backtracking"]["use_forward_checking"],
            use_ac3=config["backtracking"]["use_ac3"],
            time_limit_seconds=config["backtracking"]["time_limit_seconds"],
        )
        if positions_bt is not None:
            assert is_valid_nqueens_solution(positions_bt), (
                "backtracking returned an invalid solution"
            )
        append_result_csv(csv_path, stats_bt)
        save_solution_json(
            results_path("solutions", f"nqueens_{n}_backtracking.json"),
            positions_bt,
            stats_bt,
        )
        print(
            f"[n={n}] backtracking: solved={stats_bt.solved} time={stats_bt.time_seconds:.3f}s"
        )

        positions_sa, stats_sa = nqueens.solve_metaheuristic(
            n, seed=config["seed"], **config["metaheuristic"]
        )
        if nqueens.count_conflicts(positions_sa) == 0:
            assert is_valid_nqueens_solution(positions_sa), (
                "0 conflicts reported but solution is invalid"
            )
        append_result_csv(csv_path, stats_sa)
        save_solution_json(
            results_path("solutions", f"nqueens_{n}_metaheuristic.json"),
            positions_sa,
            stats_sa,
        )
        print(
            f"[n={n}] metaheuristic: solved={stats_sa.solved} "
            f"objective={stats_sa.objective} time={stats_sa.time_seconds:.3f}s"
        )


if __name__ == "__main__":
    main()
