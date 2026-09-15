"""Raise Python's recursion ceiling for backtrack() on large instances.

backtrack() (src/csp/backtracking.py) recurses once per assigned variable,
so a 1000-vertex graph-coloring instance can need ~1000 stack frames --
past Python's default sys.getrecursionlimit() of 1000, which raises
RecursionError well before the OS thread stack itself is actually full
(8MB by default on Linux/macOS, comfortably enough for tens of thousands
of frames from a function this small -- see `ulimit -s`). Bumping the
interpreter's own limit, not the C stack, is the actual fix here.
"""

from __future__ import annotations

import sys
from contextlib import contextmanager
from typing import Iterator


@contextmanager
def deeper_recursion(limit: int) -> Iterator[None]:
    """Temporarily raise sys.getrecursionlimit() to at least `limit`.

    Never lowers the current limit -- only raises it if `limit` is bigger
    -- and always restores the original value on exit, even if the wrapped
    code raises.
    """
    previous = sys.getrecursionlimit()
    if limit > previous:
        sys.setrecursionlimit(limit)
    try:
        yield
    finally:
        sys.setrecursionlimit(previous)
