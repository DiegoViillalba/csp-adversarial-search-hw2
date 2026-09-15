"""
Diego Vilalba 14-09-26
Wall-clock cutoff for recursive calls that have no cancellation hook of
their own (backtrack() does not accept a time budget or check one anywhere
in its recursion).


TAKEN FROM : https://pymotw.com/2/signal/

SIGALRM interrupts the interpreter wherever it happens to be — including
deep inside the recursion — and raises TimeoutError there.

"""

from __future__ import annotations

import signal
from collections.abc import Iterator
from contextlib import contextmanager


@contextmanager
def time_limit(seconds: float | None) -> Iterator[None]:
    """Raise TimeoutError if the `with` block hasn't finished after `seconds`.

    seconds=None disables the limit entirely (no alarm is armed).

    Safe to use around backtrack(): if it times out mid-recursion, the
    partially mutated `problem`/`assignment` objects are simply abandoned by
    the caller (each solve_* call builds a fresh CSP per attempt), so there
    is no cleanup to do here.
    """
    if seconds is None:
        yield
        return

    def _on_alarm(signum, frame):
        raise TimeoutError(f"timed out after {seconds}s")

    previous_handler = signal.signal(signal.SIGALRM, _on_alarm)
    # setitimer supports fractional seconds; alarm() only takes whole ints.
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        # Disarm before restoring the handler, otherwise a pending alarm
        # could fire against whatever handler/code runs right after this.
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous_handler)
