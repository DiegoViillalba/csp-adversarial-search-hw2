"""Shared plumbing for experiments/*.py runners: config/results paths, and
making `from src...` imports work no matter what directory a script is run
from (as long as it's invoked as `python experiments/run_x.py`)."""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def load_config(name: str) -> dict:
    """name e.g. "nqueens" -> loads configs/nqueens.yaml."""
    path = REPO_ROOT / "configs" / f"{name}.yaml"
    with path.open() as f:
        return yaml.safe_load(f)


def results_path(*parts: str) -> Path:
    return REPO_ROOT / "results" / Path(*parts)


def data_path(*parts: str) -> Path:
    return REPO_ROOT / "data" / Path(*parts)
