"""Instrumentation shared by every solver so results are comparable in the report.

This module is intentionally solver-agnostic: it does not know what a CSP,
a queen, or a color is. It just times things and stores numbers, so every
`src/problems/*.py` function can return the same shape of result and every
`experiments/*.py` runner can log/compare them the same way.
"""

from __future__ import annotations

import csv
import json
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class SearchStats:
    """Common result envelope for every solver in this project.

    Fields are deliberately generic:
      method:            e.g. "backtracking", "backtracking+fc+ac3", "simulated_annealing", "ortools"
      problem:           e.g. "nqueens", "graph_coloring"
      instance_size:     e.g. N for n-queens, number of vertices for coloring
      solved:            True if a valid/complete solution was found
      objective:         final value of the objective/cost function (e.g. remaining
                          conflicts, number of colors used); None if not applicable
      nodes_expanded:    backtracking-style node count; None for methods that don't
                          have this notion (e.g. OR-Tools)
      time_seconds:      wall-clock time of the solve call
      extra:             anything problem-specific worth keeping (e.g. iterations,
                          cooling schedule params, k used) that doesn't deserve its
                          own column
    """

    method: str
    problem: str
    instance_size: int
    solved: bool
    objective: float | None = None
    nodes_expanded: int | None = None
    time_seconds: float = 0.0
    extra: dict[str, Any] = field(default_factory=dict)

    def as_row(self) -> dict[str, Any]:
        row = asdict(self)
        extra = row.pop("extra")
        # Skip list/dict-valued extras (e.g. simulated_annealing's
        # energy_history: one float per iteration, easily tens of
        # thousands of entries) -- not CSV-friendly, and they'd make this
        # summary table unreadable. Still available via save_solution_json,
        # which dumps the full dataclass including extra as-is.
        row.update(
            {
                f"extra_{k}": v
                for k, v in extra.items()
                if not isinstance(v, (list, dict))
            }
        )
        return row


@contextmanager
def timer() -> Iterator[Callable[[], float]]:
    """Usage:

    with timer() as elapsed:
        do_work()
    stats.time_seconds = elapsed()
    """
    start = time.perf_counter()
    end_time = None

    def _elapsed() -> float:
        return (end_time or time.perf_counter()) - start

    try:
        yield _elapsed
    finally:
        end_time = time.perf_counter()


def append_result_csv(path: str | Path, stats: SearchStats) -> None:
    """Append one SearchStats row to a CSV in results/tables/, writing the header
    the first time the file is created.

    Different methods (e.g. backtracking vs. the metaheuristic) populate
    different keys of `stats.extra`, so the set of `extra_*` columns can
    grow between calls. Recomputing fieldnames from just the new row (the
    previous approach) silently appended rows with a different column count
    than the header. Instead, this reads back whatever rows already exist,
    unions their columns with the new row's, and rewrites the file --
    cheap here since these are small per-experiment summary tables, not a
    high-frequency log.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    row = stats.as_row()

    existing_rows: list[dict[str, Any]] = []
    fieldnames: list[str] = []
    if path.exists():
        with path.open(newline="") as f:
            existing_rows = list(csv.DictReader(f))
        if existing_rows:
            fieldnames = list(existing_rows[0].keys())

    fieldnames += [k for k in row.keys() if k not in fieldnames]

    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, restval="")
        writer.writeheader()
        writer.writerows(existing_rows)
        writer.writerow(row)


def save_solution_json(path: str | Path, solution: Any, stats: SearchStats) -> None:
    """Dump a solution + its stats to results/solutions/ for later inspection."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(
            {"solution": solution, "stats": asdict(stats)},
            f,
            indent=2,
            default=str,
        )
