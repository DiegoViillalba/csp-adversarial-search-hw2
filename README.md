# Tarea 2 — CSP, Metaheurísticas y Búsqueda con Adversarios

Inteligencia Artificial 2027-I, Posgrado en Ciencias e Ingeniería de la Computación, UNAM.

Implementación de backtracking (con revisión hacia adelante, AC3 y ordenamiento MRV/LCV),
recocido simulado, y su aplicación a N-reinas y coloreado de grafos (con comparación contra
OR-Tools). Ver `assignment.pdf` para el enunciado completo.

## Estructura del repo

```
configs/            Parámetros de cada experimento (semilla, tamaños, límites de tiempo)
  nqueens.yaml
  graph_coloring.yaml
  tic_tac_toe.yaml

src/
  csp/               Motor genérico de CSP (no sabe nada de reinas ni grafos)
    problem.py           Clase CSP: variables, dominios, is_consistent, neighbors opcional
    backtracking.py       Backtracking con hooks de heurística/forward checking
    forward_checking.py   Poda de dominios tras cada asignación
    ac3.py                 Arco-consistencia; usa problem.neighbors si está definido
                           (evita el O(V²) de probar todos los pares de variables)
    heuristics.py          mrv (selección de variable), lcv (orden de valores)

  metaheuristics/
    simulated_annealing.py Recocido simulado sobre un CSP genérico (incluye sus
                           helpers: random_complete_assignment, count_conflicts,
                           random_neighbor)

  adversarial/        Minimax / poda alfa-beta — ONGOING (ver "Estado" abajo)

  problems/            Modelado de cada problema como CSP + interfaz solve_*
    nqueens.py           build_nqueens_csp, solve_backtracking, solve_metaheuristic,
                          enumerate_solutions, count_conflicts
    graph_coloring.py     build_graph_coloring_csp, solve_backtracking,
                          solve_metaheuristic, count_conflicts
    australia_coloring.py Instancia de juguete (mapa de Australia) usada en tests
    tic_tac_toe.py        ONGOING

  integrations/
    ortools_coloring.py    Coloreado de grafos con OR-Tools (CP-SAT), baseline de comparación
    gym_tic_tac_toe.py     Wrapper sobre gym-tic-tac-toe (vendorizado en _vendor/, ver abajo)

  utils/
    random_seed.py         set_seed() — siembra random y numpy
    metrics.py              SearchStats, timer(), append_result_csv, save_solution_json
    validation.py           Verificadores independientes (is_valid_nqueens_solution, is_valid_coloring)
    graph_io.py              Lectura/escritura de grafos en el formato exacto que pide el enunciado
    timeout.py               time_limit(): corta backtrack() con SIGALRM si excede el tiempo

experiments/          Scripts ejecutables (sin argumentos, leen configs/*.yaml)
  run_nqueens.py           N-reinas N=8 y N=100, backtracking + metaheurística
  enumerate_nqueens.py      Todas las soluciones de N=100 (acotado, ver abajo)
  run_graph_coloring.py     Coloreado 50 y 1000 nodos, backtracking + metaheurística
  compare_coloring.py        + comparación contra OR-Tools
  compare_schedulers.py      Exploratorio: geometric/exponential/sinusoidal, tiempo y convergencia
  make_plots.py               Genera report/figures/*.png a partir de results/
  run_tic_tac_toe.py         ONGOING (depende de src/adversarial/ y src/problems/tic_tac_toe.py)

notebooks/
  local_results.ipynb    Corre y muestra los escenarios livianos (N=8, 50 nodos) en la laptop

scripts/
  run_remote_heavy.sh     Corre los escenarios pesados (N=100, 1000 nodos) en un servidor remoto
  run_remote_overnight.sh Exploratorio: presupuestos de horas para ver limites de computo (no pedido)

tests/                  pytest — ver "Estado" abajo para cuáles existen

report/                 Reporte en LaTeX (report.tex + sections/*.tex + references.bib)

results/                Generado al correr los experimentos (ignorado por git, ver .gitignore)
data/graphs/            Grafos generados/leídos por run_graph_coloring.py (ignorado por git)
```

## Estado

| Parte del assignment | Estado |
|---|---|
| Backtracking + revisión hacia adelante + AC3 + ordenamiento (MRV/LCV) | implementado |
| Recocido simulado | implementado |
| Minimax | ongoing (`src/adversarial/minimax.py` vacío) |
| N-reinas N=8 y N=100 (backtracking + metaheurística) | implementado |
| Todas las soluciones de N-reinas N=100 | implementado (acotado, ver abajo) |
| Coloreado de grafos 50 y 1000 nodos (backtracking + metaheurística) | implementado |
| Coloreado de grafos vs. OR-Tools | implementado |
| Gato con minimax | ongoing (`src/adversarial/`, `src/problems/tic_tac_toe.py` vacíos) |
| Ejercicios 1–4 | ver `report/sections/exercises.tex` |
| Críticas de lecturas | ver `report/sections/readings.tex` |

Tests con contenido: `test_validation.py`, `test_graph_io.py`, `test_backtracking.py` (13 casos,
todos pasan). `test_ac3.py`, `test_graph_coloring.py`, `test_minimax.py`, `test_nqueens.py` siguen
vacíos — corresponden a las partes de arriba que faltan o que aún no tienen su propio test.

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Cómo reproducir cada resultado entregado

Todo se corre desde la raíz del repo con el venv activado.

```bash
pytest                                     # corre los tests existentes (13 casos)

python experiments/run_nqueens.py          # N=8 y N=100: backtracking + recocido simulado
python experiments/enumerate_nqueens.py    # todas las soluciones de N=100 (acotado, ver abajo)
python experiments/run_graph_coloring.py   # 50 y 1000 nodos: backtracking + recocido simulado
python experiments/compare_coloring.py     # + comparación contra OR-Tools (tiempo y # colores)
python experiments/compare_schedulers.py   # exploratorio: geometric/exponential/sinusoidal
python experiments/make_plots.py           # genera las gráficas del reporte a partir de lo anterior
```

Los grafos de 50/1000 nodos se generan automáticamente en `data/graphs/` la primera vez que
corres `run_graph_coloring.py` (semilla fija en el config, reproducible). Los resultados van a
`results/tables/*.csv` (una fila por corrida, comparable entre métodos) y
`results/solutions/*` (la solución concreta encontrada, con `stats.extra.energy_history` para
las corridas del recocido simulado). `make_plots.py` lee esos archivos y deja las gráficas en
`report/figures/` — puedes correrlo las veces que quieras, se salta cualquier gráfica cuyo
archivo de entrada todavía no exista.

`python experiments/run_tic_tac_toe.py` **no corre todavía** — depende de `src/adversarial/` y
`src/problems/tic_tac_toe.py`, que siguen sin implementarse.

### Escenarios livianos vs. pesados

Los escenarios grandes (N=100 reinas, coloreado de 1000 nodos) pueden tardar minutos; se
corrieron en un servidor remoto para no ocupar la laptop mientras tanto:

- **Localmente**, `notebooks/local_results.ipynb` corre y muestra los escenarios livianos
  (N=8 reinas, coloreado de 50 nodos) directamente sobre `src/problems/*.py`.
- **En el remoto**, tras clonar este repo e instalar dependencias, `scripts/run_remote_heavy.sh`
  corre los seis comandos de arriba en background con `nohup` y deja logs en `logs/`. Sus
  resultados se traen de vuelta con `rsync` a `results/`, `data/graphs/` y `report/figures/`, y
  se usan igual que si se hubieran generado localmente — ver comentarios dentro del script para
  el uso exacto.

### Explorar límites de cómputo (no pedido por el enunciado)

`scripts/run_remote_overnight.sh` deja corriendo, en este orden, `compare_schedulers.py` (rápido,
asegura esos resultados primero) y luego dos corridas de presupuesto mucho más grande para ver
hasta dónde da el servidor: `enumerate_nqueens_overnight.py` (N=100, 5 horas) y
`run_graph_coloring_overnight.py` (coloreado de 1000 nodos, k=8, **sin** forward checking ni AC3,
55 horas — contraste directo contra la versión con heurísticas, que resuelve el mismo k en
~8.5s). Ambas escriben en archivos `*_overnight.*` separados, así que nunca pisan los resultados
de la corrida normal.

### Sobre "encontrar todas las soluciones para N=100"

El número de soluciones de N-reinas crece muy rápido (para N=27 ya son del orden de $10^{14}$);
una enumeración exhaustiva real para N=100 no es viable en el tiempo de esta tarea.
`enumerate_solutions` (en `src/problems/nqueens.py`) corta por `max_solutions` y/o
`time_limit_seconds` (ver `configs/nqueens.yaml`) y reporta honestamente si la búsqueda fue
exhaustiva o no en `stats.extra["exhaustive"]`.

## Compilar el reporte

```bash
cd report && latexmk -pdf report.tex
```
