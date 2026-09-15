"""Diego Villlba 15-09-26
Implementation of the ticktactoe game in cli
"""

import random

from src.integrations.gym_tic_tac_toe import (
    PLAYER_O,
    PLAYER_X,
    apply_move,
    is_terminal,
    is_win,
    legal_moves,
    make_env,
    get_board,
    other_player,
)
# NOTA: best_move se importa dentro de get_move(), no aqui arriba, porque
# minimax.py a su vez importa utility() de este archivo -- un import
# circular a nivel de modulo. Al diferirlo hasta que get_move() se llama,
# para entonces ambos modulos ya terminaron de cargar y el ciclo no truena.


def utility(env):
    if is_win(env, PLAYER_X):
        return 1
    if is_win(env,PLAYER_O):
        return -1
    return 0

def get_move(agent, env, player, rng):
    if agent == 'minimax':
        from src.adversarial.minimax import best_move

        return best_move(env,player)
    if agent == 'random':
        # legal_moves(env), no legal_moves -- rng.choice necesita la lista de
        # movimientos, no la funcion misma
        return rng.choice(legal_moves(env))
    else:
        raise NotImplementedError


def play_game(agent_x, agent_o, env_kwargs = None, seed=None, render = False):
    env = make_env(**(env_kwargs or {}))
    rng = random.Random(seed)

    # We respevt the convention in the gym code

    current_player = PLAYER_X

    movements = []
    board_history = [get_board(env)]

    while not is_terminal(env):
        agent = agent_x if current_player == PLAYER_X else agent_o
        move = get_move(agent, env, current_player, rng)

        apply_move(env, current_player, move)
        movements.append(move)
        board_history.append(get_board(env))

        if render:
            print(get_board(env))

        current_player = other_player(current_player)

    if is_win(env, PLAYER_X):
        winner = PLAYER_X
    elif is_win(env, PLAYER_O):
        winner = PLAYER_O
    else:
        winner = None

    return {
        "moves": movements,
        "winner": winner,
        "board_history": board_history,
    }
