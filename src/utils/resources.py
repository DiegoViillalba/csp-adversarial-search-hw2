"""Peak memory usage, for characterizing how a search performed -- used by
the overnight scripts (experiments/*_overnight.py) alongside nodes_expanded
to actually evaluate compute limits, not just wall-clock time.

Uses resource.getrusage() (stdlib, no extra dependency) rather than
tracemalloc: it reports the WHOLE PROCESS's peak resident set size, which
is what matters for "did this fit in the machine's RAM". tracemalloc only
tracks Python-level object allocation, missing e.g. the C-level interpreter
overhead of thousands of stacked backtrack() frames.
"""

from __future__ import annotations

import resource
import sys


def peak_memory_mb() -> float:
    """Peak resident set size of THIS PROCESS so far, in MB.

    Monotonically non-decreasing across the whole process's lifetime (the
    OS only reports the high-water mark, not a per-call delta) -- accurate
    as "how much did this search need" when it's the only significant thing
    the process has done, which is how the overnight scripts use it (one
    process, one search, read this once at the end).
    """
    raw = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # Linux reports ru_maxrss in KB, macOS (darwin) reports it in bytes --
    # same struct field, different units depending on the OS.
    if sys.platform == "darwin":
        return raw / (1024 * 1024)
    return raw / 1024
