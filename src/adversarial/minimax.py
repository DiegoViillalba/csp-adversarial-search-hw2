"""Diego Villalba 15-09-26

tic tac toe implemetatiotn using gymnasium tac toe from open ai

check the repo :
https://github.com/LudwigStumpp/gym-tic-tac-toe

I decided to create an interface to make a cleeaner looking code
the intrfaz lives inside integrations/gym_tic_tac_toe
"""

from src.integrations.gym_tic_tac_toe import (
    PLAYER_O,
    PLAYER_X,
    apply_move,
    clone_env,
    is_full,
    is_terminal,
    legal_moves,
    other_player,
)
from src.problems.tic_tac_toe import utility


def mini_max(env, player):
    if is_terminal(env) or is_full(env):
        return utility(env)

    if player == PLAYER_X:
        best_value = float("-inf")
        for movement in legal_moves(env):
            child = clone_env(env)
            apply_move(child, player, movement)
            best_value = max(best_value, mini_max(child, other_player(player)))
        return best_value
    else:
        least_value = float("inf")
        for movement in legal_moves(env):
            child = clone_env(env)
            apply_move(child, player, movement)
            least_value = min(least_value, mini_max(child, other_player(player)))
        return least_value


def best_move(env, player):
    if player == PLAYER_X:
        best_value = float("-inf")
    else:
        best_value = float("inf")

    best_move = None

    for move in legal_moves(env):
        child = clone_env(env)
        apply_move(child, player, move)
        value = mini_max(child, other_player(player))

        if value is None:
            continue

        if (player == PLAYER_X and value > best_value) or (
            player == PLAYER_O and value < best_value
        ):
            best_value = value
            best_move = move

    return best_move
