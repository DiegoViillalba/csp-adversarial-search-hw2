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
        row.update({f"extra_{k}": v for k, v in extra.items()})
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
    the first time the file is created."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    row = stats.as_row()
    file_exists = path.exists()
    with path.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if not file_exists:
            writer.writeheader()
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
