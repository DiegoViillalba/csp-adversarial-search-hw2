"""Extra (no forma parte de la calificación de la tarea): interfaz grafica en
pygame para jugar gato contra el agente de minimax ya implementado.

Requiere: pip install pygame (no esta en requirements.txt a proposito, es un
bonus, no una dependencia del entregable).

Como correrlo:
    python play_pygame.py

Diseno: pygame NO sabe nada de reglas del juego. Solo hace dos cosas:
    1. dibuja lo que get_board(env) le dice que hay en el tablero.
    2. traduce un clic de mouse a un indice de celda (0-8) y llama a
       apply_move con ese indice.
Toda la logica real (movimientos legales, terminacion, quien gano, cual es
la mejor jugada) sigue viviendo en src/integrations/gym_tic_tac_toe.py y
src/adversarial/minimax.py, exactamente igual que en el resto del proyecto.
Esta es la misma separacion motor/interfaz que CSP <-> backtracking.py, o
tic_tac_toe.py <-> minimax.py.
"""

import sys

import pygame

from src.adversarial.minimax import best_move
from src.integrations.gym_tic_tac_toe import (
    PLAYER_O,
    PLAYER_X,
    apply_move,
    get_board,
    is_terminal,
    is_win,
    legal_moves,
    make_env,
    other_player,
)

# _____ Constantes visuales _____

WINDOW_SIZE = 300  # ventana cuadrada
CELL_SIZE = WINDOW_SIZE // 3  # 3x3, cada celda mide lo mismo
LINE_WIDTH = 6
MARK_MARGIN = 20  # espacio entre el borde de la celda y el simbolo dibujado

COLOR_BG = (245, 245, 245)
COLOR_LINES = (30, 30, 30)
COLOR_X = (200, 40, 40)
COLOR_O = (40, 90, 200)
COLOR_TEXT = (20, 20, 20)

HUMAN = PLAYER_X  # el humano siempre juega X y mueve primero
AI = PLAYER_O  # minimax juega O


def draw_grid(screen: pygame.Surface) -> None:
    """Dibuja las 2 lineas verticales y 2 horizontales que separan las 9 celdas."""
    for i in (1, 2):
        # vertical en x = i * CELL_SIZE, de arriba a abajo
        pygame.draw.line(
            screen,
            COLOR_LINES,
            (i * CELL_SIZE, 0),
            (i * CELL_SIZE, WINDOW_SIZE),
            LINE_WIDTH,
        )
        # horizontal en y = i * CELL_SIZE, de izquierda a derecha
        pygame.draw.line(
            screen,
            COLOR_LINES,
            (0, i * CELL_SIZE),
            (WINDOW_SIZE, i * CELL_SIZE),
            LINE_WIDTH,
        )


def draw_marks(screen: pygame.Surface, env) -> None:
    """Recorre get_board(env) (0=vacio, 1=X, 2=O) y dibuja el simbolo que
    corresponda en cada celda. Esta es la unica funcion que "lee" el estado
    del juego para pintarlo -- nunca modifica env."""
    board = get_board(env)
    for row in range(3):
        for col in range(3):
            value = board[row][col]
            if value == 0:
                continue

            # esquina superior-izquierda de la celda (col, row) en pixeles
            x0 = col * CELL_SIZE
            y0 = row * CELL_SIZE

            if value == PLAYER_X:
                # dibuja una X: dos lineas diagonales dentro de la celda
                pygame.draw.line(
                    screen,
                    COLOR_X,
                    (x0 + MARK_MARGIN, y0 + MARK_MARGIN),
                    (x0 + CELL_SIZE - MARK_MARGIN, y0 + CELL_SIZE - MARK_MARGIN),
                    LINE_WIDTH,
                )
                pygame.draw.line(
                    screen,
                    COLOR_X,
                    (x0 + CELL_SIZE - MARK_MARGIN, y0 + MARK_MARGIN),
                    (x0 + MARK_MARGIN, y0 + CELL_SIZE - MARK_MARGIN),
                    LINE_WIDTH,
                )
            else:  # PLAYER_O
                center = (x0 + CELL_SIZE // 2, y0 + CELL_SIZE // 2)
                radius = CELL_SIZE // 2 - MARK_MARGIN
                pygame.draw.circle(screen, COLOR_O, center, radius, LINE_WIDTH)


def cell_index_from_mouse(pos: tuple[int, int]) -> int:
    """Traduce un clic en pixeles (x, y) al indice de celda 0-8 que espera
    apply_move (row-major, igual que legal_moves)."""
    x, y = pos
    col = x // CELL_SIZE
    row = y // CELL_SIZE
    return row * 3 + col


def show_message(screen: pygame.Surface, text: str) -> None:
    """Overlay simple con el resultado final, centrado en la ventana."""
    font = pygame.font.SysFont(None, 36)
    surface = font.render(text, True, COLOR_TEXT, (255, 255, 255))
    rect = surface.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2))
    screen.blit(surface, rect)


def winner_text(env) -> str:
    if is_win(env, PLAYER_X):
        return "Gano X"
    if is_win(env, PLAYER_O):
        return "Gano O"
    return "Empate"


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("Gato - tu (X) vs minimax (O)")
    clock = pygame.time.Clock()

    env = make_env()
    current_player = PLAYER_X  # X siempre empieza

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # solo reaccionamos a clics cuando le toca al humano y el
            # juego sigue activo -- mientras el turno es de la IA, los
            # clics simplemente se ignoran
            elif (
                event.type == pygame.MOUSEBUTTONDOWN
                and current_player == HUMAN
                and not is_terminal(env)
            ):
                cell = cell_index_from_mouse(event.pos)
                if cell in legal_moves(env):
                    apply_move(env, HUMAN, cell)
                    current_player = other_player(current_player)

        # turno de la IA: se resuelve de inmediato (sin esperar un evento)
        # apenas detectamos que le toca. Como current_player cambia dentro
        # de este mismo if, en el siguiente frame ya no vuelve a entrar aqui
        # -- no hace falta ninguna bandera extra para "jugar una sola vez".
        if current_player == AI and not is_terminal(env):
            move = best_move(env, AI)
            apply_move(env, AI, move)
            current_player = other_player(current_player)

        screen.fill(COLOR_BG)
        draw_grid(screen)
        draw_marks(screen, env)

        if is_terminal(env):
            show_message(screen, winner_text(env))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
