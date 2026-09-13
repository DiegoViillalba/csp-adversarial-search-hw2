# Tarea 2 — CSP, Metaheurísticas y Búsqueda con Adversarios

## División del trabajo

Andamiaje ya armado (I/O, configs, runners, integraciones, reporte):

- `src/utils/` — `random_seed.py`, `metrics.py` (`SearchStats`, `timer()`, guardado de resultados), `validation.py` (verificadores independientes), `graph_io.py` (formato de E/S exacto que pide el enunciado + generador de grafos aleatorios).
- `src/integrations/ortools_coloring.py` — coloreado de grafos con OR-Tools (CP-SAT), listo para usar.
- `src/integrations/gym_tic_tac_toe.py` + `src/integrations/_vendor/gym_tictactoe/` — wrapper sobre el repo [gym-tic-tac-toe](https://github.com/LudwigStumpp/gym-tic-tac-toe) (vendorizado localmente porque su `setup.py` no declara `packages=`, así que un `pip install` normal de ese repo no instala nada — ver `_vendor/gym_tictactoe/LICENSE`).
- `experiments/*.py` — runners que cargan `configs/*.yaml`, llaman tu código, validan la solución de forma independiente y guardan resultados en `results/`.
- `configs/*.yaml`, `report/report.tex` + `report/sections/*.tex` (estructura y TODOs, sin contenido) + `report/references.bib` (las dos lecturas ya citadas correctamente).
- `tests/test_validation.py`, `tests/test_graph_io.py` — ejemplo del patrón de test a seguir.
- Ya corrí `pytest` y pruebas manuales de cada pieza de andamiaje — todo importa y funciona.

Por escribir (el núcleo algorítmico — aquí están el aprendizaje y los puntos):

- `src/csp/problem.py`, `backtracking.py`, `forward_checking.py`, `ac3.py`, `heuristics.py`
- `src/metaheuristics/base.py`, `simulated_annealing.py`
- `src/adversarial/minimax.py`, `alpha_beta.py`
- `src/problems/nqueens.py`, `graph_coloring.py`, `tic_tac_toe.py` — el modelado de cada problema (variables/dominio/restricciones, o estado/vecindad/objetivo) también es tuyo; es la misma pregunta que el Ejercicio 1.
- `tests/test_backtracking.py`, `test_ac3.py`, `test_graph_coloring.py`, `test_minimax.py`, `test_nqueens.py`
- Contenido del reporte (`report/sections/*.tex`): críticas, ejercicios, discusión de resultados.

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Ya está creado un `.venv/` funcional en esta carpeta (ignorado por git); solo actívalo con `source .venv/bin/activate`.

## Cómo correr cada experimento

Todos se corren desde `hw2/` con el venv activado:

```bash
python experiments/run_nqueens.py          # N=8 y N=100, backtracking + metaheurística
python experiments/enumerate_nqueens.py    # todas las soluciones N=100 (acotado, ver abajo)
python experiments/run_graph_coloring.py   # 50 y 1000 nodos, backtracking + metaheurística
python experiments/compare_coloring.py     # + OR-Tools, tabla comparativa
python experiments/run_tic_tac_toe.py      # partidas con minimax/alpha-beta
pytest                                     # corre todos los tests
```

Los grafos de 50/1000 nodos se generan automáticamente en `data/graphs/` la primera vez que corres `run_graph_coloring.py` (semilla fija en el config, reproducible). Resultados van a `results/tables/` (CSV) y `results/solutions/` (JSON / formato de salida pedido).

## Sobre "encontrar todas las soluciones para N=100"

El número de soluciones de N-reinas crece muy rápido (para N=27 ya son del orden de $10^{14}$); para N=100 una enumeración exhaustiva real no es viable en el tiempo de esta tarea. `enumerate_nqueens.py` está pensado para que tu `enumerate_solutions` corte por `max_solutions` y/o `time_limit_seconds` (ver `configs/nqueens.yaml`) y reporte honestamente si la búsqueda fue exhaustiva o no (`stats.extra["exhaustive"]`). Vale la pena que el reporte discuta esto explícitamente en vez de intentar forzar una enumeración completa.

## Interfaces esperadas

Los runners en `experiments/` llaman estas funciones. Firmas exactas — impleméntalas así para que todo conecte sin tocar el andamiaje. El diseño interno de `src/csp/`, `src/metaheuristics/`, `src/adversarial/` es enteramente tuyo; esto es solo el límite hacia afuera.

Usa `src.utils.metrics.SearchStats` y `src.utils.metrics.timer()` dentro de tus funciones `solve_*` para construir el objeto de estadísticas que devuelves.

### `src/problems/nqueens.py`

```python
def solve_backtracking(
    n: int,
    use_forward_checking: bool,
    use_ac3: bool,
    time_limit_seconds: float | None,
) -> tuple[list[int] | None, SearchStats]:
    """positions[col] = row. None si no se encontró solución (o se agotó el tiempo)."""


def solve_metaheuristic(
    n: int, seed: int | None, **params
) -> tuple[list[int], SearchStats]:
    """Mejor asignación encontrada (puede tener conflictos — revisa stats.objective)."""


def enumerate_solutions(
    n: int, max_solutions: int | None, time_limit_seconds: float | None
) -> tuple[list[list[int]], SearchStats]:
    """Todas las soluciones encontradas hasta el primer límite alcanzado.
    stats.extra["exhaustive"]: bool, si la búsqueda terminó sola o fue cortada."""


def count_conflicts(positions: list[int]) -> int:
    """Pares de reinas atacándose — tu función objetivo."""
```

### `src/problems/graph_coloring.py`

```python
def solve_backtracking(
    num_vertices: int,
    edges: list[tuple[int, int]],
    k: int,
    use_forward_checking: bool,
    use_ac3: bool,
    time_limit_seconds: float | None,
) -> tuple[dict[int, int] | None, SearchStats]:
    """Coloreado propio con k colores, o None si es infactible / se agota el tiempo."""


def solve_metaheuristic(
    num_vertices: int,
    edges: list[tuple[int, int]],
    k: int,
    seed: int | None,
    **params,
) -> tuple[dict[int, int], SearchStats]:
    """Mejor coloreado encontrado usando exactamente k colores (puede tener
    conflictos — revisa stats.objective)."""


def count_conflicts(
    edges: list[tuple[int, int]], coloring: dict[int, int]
) -> int:
    """Aristas con extremos del mismo color — tu función objetivo."""
```

`experiments/run_graph_coloring.py` y `compare_coloring.py` ya hacen la búsqueda del k mínimo factible (iterando `k_min..k_max` del config) sobre estas dos funciones — no lo repitas dentro de `graph_coloring.py`.

### `src/problems/tic_tac_toe.py`

```python
def play_game(
    agent_x: str,
    agent_o: str,
    env_kwargs: dict | None,
    seed: int | None,
    render: bool,
) -> dict:
    """agent_x/agent_o en {"minimax", "alpha_beta", "random"}.
    env_kwargs se pasa a src.integrations.gym_tic_tac_toe.make_env(**env_kwargs).
    Devuelve {"moves": [...], "winner": int | None, "board_history": [...]}."""
```

Construye el `env` con `src.integrations.gym_tic_tac_toe.make_env`, usa `clone_env`/`legal_moves`/`apply_move`/`is_terminal`/`is_win` de ese mismo módulo para no reimplementar las reglas del juego, y llama tu `minimax`/`alpha_beta` para decidir cada jugada.

## Compilar el reporte

```bash
cd report && latexmk -pdf report.tex
```

## Ruta de implementación sugerida (para terminar en un día)

1. `src/csp/problem.py` + `backtracking.py` — valida con un CSP de juguete o N=4/8 antes de escalar.
2. `heuristics.py`, `forward_checking.py`, `ac3.py` — necesarios para que N=100 reinas y el coloreado de 1000 nodos terminen en tiempo razonable.
3. `src/problems/nqueens.py` sobre el motor anterior → corre `run_nqueens.py` y `enumerate_nqueens.py`.
4. `src/problems/graph_coloring.py` reusando el mismo motor → corre `run_graph_coloring.py` y `compare_coloring.py` (OR-Tools ya está listo).
5. `src/metaheuristics/base.py` + `simulated_annealing.py`, aplicado en ambos `problems/*.py` (ya deberían tener `solve_metaheuristic`).
6. `src/adversarial/minimax.py` + `alpha_beta.py` → `src/problems/tic_tac_toe.py` → corre `run_tic_tac_toe.py`.
7. Ejercicios 1 y 2 (CSP/búsqueda local) — mejor justo después del paso 2-5, con el tema fresco.
8. Ejercicios 3 y 4 (árbol de juego, prueba de alfa-beta) — mejor justo después del paso 6, ya con alfa-beta implementado.
9. Críticas de lecturas + integración final del reporte.
