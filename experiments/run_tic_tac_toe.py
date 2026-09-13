"""Plays tic-tac-toe games with minimax/alpha-beta agents on the
gym-tic-tac-toe env, per configs/tic_tac_toe.yaml, and saves the trace(s).

Expects src/problems/tic_tac_toe.py to expose:
    play_game(agent_x, agent_o, env_kwargs=None, seed=None, render=False) -> dict
        {"moves": [...], "winner": int | None, "board_history": [...]}
    where agent_x/agent_o in {"minimax", "alpha_beta", "random"}, and
    env_kwargs is passed to src.integrations.gym_tic_tac_toe.make_env.
See README.md ("Interfaces esperadas") for the full contract.
"""

from __future__ import annotations

import json

from _common import load_config, results_path

from src.problems import tic_tac_toe
from src.utils.random_seed import set_seed


def main() -> None:
    config = load_config("tic_tac_toe")
    set_seed(config["seed"])

    games = []
    for i in range(config["num_games"]):
        trace = tic_tac_toe.play_game(
            agent_x=config["agents"]["player_1"],
            agent_o=config["agents"]["player_2"],
            env_kwargs=config["env"],
            seed=config["seed"] + i,
            render=config["render"],
        )
        games.append(trace)
        print(f"game {i}: winner={trace['winner']} moves={len(trace['moves'])}")

    out_path = results_path("solutions", "tic_tac_toe_games.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w") as f:
        json.dump(games, f, indent=2, default=str)


if __name__ == "__main__":
    main()
