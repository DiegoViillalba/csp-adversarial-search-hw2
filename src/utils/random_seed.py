"""Reproducibility helper: seed every RNG the project touches from one place."""

from __future__ import annotations

import random

import numpy as np


def set_seed(seed: int) -> None:
    """Seed Python's ``random`` and ``numpy`` so a run can be reproduced.

    Call this once at the start of every experiment/script, using the seed
    from the relevant config file.
    """
    random.seed(seed)
    np.random.seed(seed)
