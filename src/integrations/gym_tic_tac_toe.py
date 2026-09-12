"""Thin, mechanical wrapper around the vendored gym-tic-tac-toe env
(https://github.com/LudwigStumpp/gym-tic-tac-toe, see src/integrations/_vendor/).

This module only exposes primitives: board state, legal moves, win/draw
checks, cloning, stepping. It does NOT define a utility function or call
minimax — that modeling step (actions, result, terminal-test, utility)
belongs in src/problems/tic_tac_toe.py, the same way nqueens.py/
graph_coloring.py model their problems on top of the src/csp/ engine.

Note: the vendored env exposes _decode/_is_win/_is_full as "private" methods
and has no public terminal-test/utility API — we lean on them deliberately
here rather than reimplementing win-checking logic a second time.
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path
from typing import Any

_VENDOR_DIR = Path(__file__).parent / "_vendor"
if str(_VENDOR_DIR) not in sys.path:
    sys.path.insert(0, str(_VENDOR_DIR))

from gym_tictactoe.envs.tictactoe_env import TictactoeEnv  # noqa: E402

Board = tuple[tuple[int, ...], ...]

PLAYER_X = 1  # moves first
PLAYER_O = 2


def make_env(size: int = 3, num_winning: int = 3, **reward_kwargs: Any) -> TictactoeEnv:
    env = TictactoeEnv(size=size, num_winning=num_winning, **reward_kwargs)
    env.reset()
    return env


def clone_env(env: TictactoeEnv) -> TictactoeEnv:
    """Deep-copy so minimax/alpha-beta can explore hypothetical moves without
    mutating the real game. The board is tiny, so a deepcopy per search node
    is cheap enough — no need for an incremental undo-move."""
    return copy.deepcopy(env)


def get_board(env: TictactoeEnv) -> Board:
    """size x size grid, immutable/hashable: 0 = empty, 1 = X (first mover), 2 = O."""
    return tuple(tuple(row) for row in env._decode(env.s))


def legal_moves(env: TictactoeEnv) -> list[int]:
    """Free board positions, 0-indexed, row-major."""
    return env.get_valid_moves()


def apply_move(env: TictactoeEnv, player: int, position: int) -> tuple[int, float, bool, str]:
    """Mutates `env` in place. `player` is 1 (X) or 2 (O) — this wrapper does the
    1/2 -> 0/1 translation the underlying env.step() expects.

    Returns (observation, reward, done, info) straight from env.step().
    """
    if player not in (PLAYER_X, PLAYER_O):
        raise ValueError(f"player must be {PLAYER_X} or {PLAYER_O}, got {player}")
    return env.step([player - 1, position])


def is_win(env: TictactoeEnv, player: int) -> bool:
    return env._is_win(player)


def is_full(env: TictactoeEnv) -> bool:
    return env._is_full()


def is_terminal(env: TictactoeEnv) -> bool:
    return is_full(env) or is_win(env, PLAYER_X) or is_win(env, PLAYER_O)


def other_player(player: int) -> int:
    return PLAYER_O if player == PLAYER_X else PLAYER_X
