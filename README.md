# Tarea 2 — CSP, Metaheurísticas y Búsqueda con Adversarios

Inteligencia Artificial 2027-I, Posgrado en Ciencias e Ingeniería de la Computación, UNAM.
Ver [`assignment.pdf`](assignment.pdf) para el enunciado completo.

Implementación de backtracking (con revisión hacia adelante, AC-3 y ordenamiento MRV/LCV),
recocido simulado y minimax, aplicados a N-reinas, coloreado de grafos (con comparación contra
OR-Tools) y tic-tac-toe (`gym-tic-tac-toe`), más los 4 ejercicios y las 2 críticas de lectura
pedidas por el enunciado.

**Todo el enunciado está resuelto.** El reporte en PDF (`report/report.pdf`, fuente en
`report/report.tex`) es el entregable formal y contiene, explícitamente, qué partes se
resolvieron (su primera sección, "Partes resueltas", es una tabla con esa lista y su referencia
cruzada); este README es el mapa código ↔ reporte ↔ notebook para quien quiera verificar o
reproducir cualquier resultado.

## Mapa: enunciado → código → reporte → notebook

| # | Parte del enunciado (puntos) | Código | Reporte (`report/report.tex`) | Notebook (`notebooks/results.ipynb`) |
|---|---|---|---|---|
| 1 | Crítica: Tönshoff et al. 2023 (5) | — (lectura) | §"Crítica de lecturas" › Tönshoff | — |
| 2 | Crítica: Doerr et al. 2024 (5) | — (lectura) | §"Crítica de lecturas" › Doerr | — |
| 3 | Backtracking + rev. adelante + AC-3 + ordenamiento (20) | [`src/csp/problem.py`](src/csp/problem.py), [`backtracking.py`](src/csp/backtracking.py), [`forward_checking.py`](src/csp/forward_checking.py), [`ac3.py`](src/csp/ac3.py), [`heuristics.py`](src/csp/heuristics.py) | §"Implementación" › CSP genérico | Sección 1 |
| 4 | Recocido simulado (20) | [`src/metaheuristics/simulated_annealing.py`](src/metaheuristics/simulated_annealing.py) | §"Implementación" › Metaheurística | Sección 1 |
| 5 | Minimax (5) | [`src/adversarial/minimax.py`](src/adversarial/minimax.py) | §"Implementación" › Minimax | Secciones 1 y 6 |
| 6 | N-reinas N=8 y N=100 (backtracking + metaheurística) (5) | [`src/problems/nqueens.py`](src/problems/nqueens.py) | §"Aplicación" › N-reinas | Sección 2 |
| 7 | Todas las soluciones N-reinas N=100 (5) | `nqueens.enumerate_solutions` (mismo archivo) | §"Aplicación" › Todas las soluciones | Sección 3 |
| 8 | Coloreado de grafos 50 y 1000 nodos (backtracking + metaheurística) (5) | [`src/problems/graph_coloring.py`](src/problems/graph_coloring.py) | §"Aplicación" › Coloreado de grafos | Sección 4 |
| 9 | Coloreado vs. OR-Tools (5) | [`src/integrations/ortools_coloring.py`](src/integrations/ortools_coloring.py) | §"Aplicación" › Coloreado vs. OR-Tools | Sección 5 |
| 10 | Gato (`gym-tic-tac-toe`) con minimax (5) | [`src/integrations/gym_tic_tac_toe.py`](src/integrations/gym_tic_tac_toe.py), [`src/problems/tic_tac_toe.py`](src/problems/tic_tac_toe.py) | §"Aplicación" › Gato | Sección 6 |
| 11 | Ejercicio 1: caballos como CSP (5) | — (papel/formulación) | §"Ejercicios" › Ejercicio 1 | — |
| 12 | Ejercicio 2: Sudoku con búsqueda local (5) | — (discusión) | §"Ejercicios" › Ejercicio 2 | — |
| 13 | Ejercicio 3: árbol de juego del gato (5) | verificado contra `mini_max` real, sección 6 del notebook | §"Ejercicios" › Ejercicio 3 | Sección 6 (verificación cruzada) |
| 14 | Ejercicio 4: correctud de poda alfa-beta (5) | — (prueba formal) | §"Ejercicios" › Ejercicio 4 | — |

Los ejercicios y las críticas de lectura son papel/matemáticas por naturaleza — no producen
código ejecutable propio, así que viven únicamente en el reporte (no hay nada que "correr" para
ellos, salvo el Ejercicio 3, cuya verificación empírica sí se corre en la sección 6 del
notebook). Todo lo demás tiene código real, se corre, y aparece en el notebook.

## Estructura del repo

```
configs/                Parámetros de cada experimento (semilla, tamaños, límites de tiempo)
  nqueens.yaml
  graph_coloring.yaml
  tic_tac_toe.yaml

src/
  csp/                  Motor genérico de CSP (no sabe nada de reinas, grafos ni gatos)
    problem.py             Clase CSP: variables, dominios, is_consistent, neighbors opcional
    backtracking.py         backtrack(): recursivo, hooks de heurística/orden/forward checking,
                            find_all=True + solutions_accumulator para enumerar todas las soluciones
    forward_checking.py     Poda de dominios tras cada asignación (forward_check/restore_domains)
    ac3.py                   Arco-consistencia (revise/ac3); usa problem.neighbors si existe
                            (evita el O(V²) de probar todos los pares de variables)
    heuristics.py            mrv (selección de variable), lcv (orden de valores)

  metaheuristics/
    simulated_annealing.py  Recocido simulado sobre un CSP genérico: random_complete_assignment,
                            count_conflicts incremental, random_neighbor, Metropolis-accept,
                            3 agendas de enfriamiento (geometric/exponential/sinusoidal)

  adversarial/
    minimax.py              mini_max(env, player) y best_move(env, player) — acoplados a
                            gym_tic_tac_toe (no genéricos; ver §"Implementación" del reporte)
    alpha_beta.py            Vacío a propósito: el rubro de implementación (45 pts) solo pide
                            Minimax; alfa-beta se resuelve en teoría en el Ejercicio 4

  problems/                Modelado de cada problema como CSP + interfaz solve_*
    nqueens.py               build_nqueens_csp, solve_backtracking, solve_metaheuristic,
                            enumerate_solutions (reusa backtrack con find_all=True), count_conflicts
    graph_coloring.py         build_graph_coloring_csp, solve_backtracking, solve_metaheuristic,
                            count_conflicts
    tic_tac_toe.py             utility(env), get_move(agent, env, player, rng), play_game(...)
    australia_coloring.py     Instancia de juguete (mapa de Australia) usada en tests

  integrations/
    ortools_coloring.py       Coloreado de grafos con OR-Tools (CP-SAT): solve_coloring_ortools,
                            find_min_colors_ortools — baseline de comparación pedido por el enunciado
    gym_tic_tac_toe.py         Wrapper delgado sobre gym-tic-tac-toe (vendorizado en _vendor/):
                            solo mecánica de tablero, nada de utilidad/minimax
    _vendor/gym_tictactoe/     https://github.com/LudwigStumpp/gym-tic-tac-toe, vendorizado tal cual

  utils/
    random_seed.py           set_seed() — siembra random y numpy
    metrics.py                 SearchStats, timer(), append_result_csv, save_solution_json
    validation.py               Verificadores independientes (is_valid_nqueens_solution, is_valid_coloring)
    graph_io.py                  read_graph/write_graph/write_coloring en el formato EXACTO del
                                enunciado (línea 1 = vértices aristas; salida = colores usados,
                                luego "color vértice" por línea) + generate_random_graph
    timeout.py                   time_limit(): corta backtrack() con SIGALRM si excede el tiempo
    recursion.py                  deeper_recursion(): sube sys.setrecursionlimit() para instancias grandes
    resources.py                   peak_memory_mb() — memoria pico del proceso (scripts *_overnight.py)

experiments/            Scripts ejecutables (sin argumentos, leen configs/*.yaml)
  run_nqueens.py            N-reinas N=8 y N=100, backtracking + recocido simulado
  enumerate_nqueens.py       Todas las soluciones de N=100 (acotado, ver notebook sección 3)
  run_graph_coloring.py      Coloreado 50 y 1000 nodos, backtracking + recocido simulado
  compare_coloring.py         + comparación contra OR-Tools
  run_tic_tac_toe.py          Corre partidas según configs/tic_tac_toe.yaml, guarda el historial
  compare_schedulers.py       Exploratorio: geometric/exponential/sinusoidal, tiempo y convergencia
  make_plots.py                Genera report/figures/*.png a partir de results/
  *_overnight.py                Exploratorio, no pedido por el enunciado — ver notebook sección 7
                                y comentarios de cada script para el porqué de cada uno

notebooks/
  results.ipynb            Notebook único, organizado por sección del enunciado (índice al
                            inicio): corre en vivo los escenarios livianos (N=8, 50 nodos),
                            lee los resultados pesados/de exploración traídos del remoto, y dejó
                            una comparación completa contra OR-Tools + tic-tac-toe con minimax

scripts/
  push_graphs_remote.sh     Sube gc_50_7.txt/gc_1000_9.txt al remoto (data/graphs/ es gitignored)
  run_remote_heavy.sh        Corre los escenarios pesados (N=100, 1000 nodos) en el servidor remoto
  run_remote_overnight.sh     Exploratorio: presupuestos de horas para ver límites de cómputo (no pedido)

tests/                  pytest — 13 pruebas, todas pasan (ver "Estado de las pruebas" abajo)

report/                 report.tex (documento único, sin \input — ver nota abajo) + report.pdf
                        (compilado, gitignored) + figures/*.png + references.bib

results/                Generado al correr los experimentos (ignorado por git)
data/graphs/            gc_50_7.txt / gc_1000_9.txt (instancias oficiales) + grafos de prueba (ignorado por git)
```

### Nota: `report/report.tex` es un documento único

`report/report.tex` contiene **todo** el reporte (crítica de lecturas, implementación,
aplicación, ejercicios, reproducibilidad, conclusiones, bibliografía) en un solo archivo, sin
`\input`/`\include`. Los archivos en `report/sections/*.tex` (`csp.tex`, `metaheuristics.tex`,
`adversarial.tex`, `exercises.tex`, `readings.tex`, `conclusions.tex`) son **restos de una
estructura modular anterior y ya no se usan en la compilación** — algunos todavía tienen
placeholders `% TODO` desactualizados que contradicen el reporte real. No afectan el PDF
entregado (`report/report.pdf` se genera solo de `report.tex`), pero conviene que lo sepas antes
de entregar: si quieres, puedo borrarlos en un commit aparte para que no confundan a quien revise
el repo — dime y lo hago.

## Estado de las pruebas

`pytest` — **13 pruebas, todas pasan**: `test_validation.py`, `test_graph_io.py`,
`test_backtracking.py` tienen casos reales. `test_ac3.py`, `test_graph_coloring.py`,
`test_minimax.py`, `test_nqueens.py` existen pero están vacíos (no es un requisito del
enunciado — la corrección de estas partes se verifica en su lugar con los asserts
`is_valid_*`/`is_win` dentro de cada script de `experiments/` y del notebook, más las
validaciones cruzadas descritas abajo).

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Cómo reproducir cada resultado

Todo se corre desde la raíz del repo (`hw2/`) con el venv activado.

```bash
pytest                                     # 13 pruebas unitarias

python experiments/run_nqueens.py          # N=8 y N=100: backtracking + recocido simulado
python experiments/enumerate_nqueens.py    # todas las soluciones de N=100 (acotado)
python experiments/run_tic_tac_toe.py      # partidas minimax vs. minimax (configs/tic_tac_toe.yaml)
python experiments/run_graph_coloring.py   # 50 y 1000 nodos: backtracking + recocido simulado
python experiments/compare_coloring.py     # + comparación contra OR-Tools
python experiments/compare_schedulers.py   # exploratorio: geometric/exponential/sinusoidal
python experiments/make_plots.py           # genera las gráficas del reporte a partir de lo anterior
```

Los grafos de 50/1000 nodos son los provistos para la tarea (`data/graphs/gc_50_7.txt`,
`gc_1000_9.txt`; `data/graphs/` está en `.gitignore`, así que si clonas el repo desde cero
necesitas copiarlos ahí tú mismo — ver `assignment.pdf`/el enunciado original para obtenerlos).
Los resultados van a `results/tables/*.csv` (una fila por corrida) y `results/solutions/*` (la
solución concreta, en el formato exacto que pide el enunciado para coloreado de grafos: primera
línea = número de colores usados, líneas siguientes = `color vértice`). `make_plots.py` lee esos
archivos y deja las gráficas en `report/figures/`; se puede correr las veces que se quiera, se
salta cualquier gráfica cuyo archivo de entrada todavía no exista.

**Advertencia de tiempo**: `run_graph_coloring.py`/`compare_coloring.py` corren el barrido de
`k` para **ambas** instancias, incluida `gc_1000_9.txt` (1000 nodos, 449,735 aristas) — dado que
ni backtracking ni el recocido simulado resuelven esa instancia en un tiempo razonable (ver
notebook sección 4 y `report/report.tex` §"Aplicación"), correr esto tal cual sobre la instancia
grande puede tardar horas. Los resultados reales para 1000 nodos ya están en el repo
(`results/tables/`, generados en el servidor remoto vía `scripts/run_remote_heavy.sh` — ver
`scripts/*.sh` para el flujo exacto) y son los que usan tanto el reporte como el notebook.

### Escenarios livianos vs. pesados

- **Localmente**, `notebooks/results.ipynb` corre en vivo los escenarios livianos (N=8 reinas,
  coloreado de 50 nodos, tic-tac-toe) directamente sobre `src/problems/*.py`.
- **En el remoto**, `scripts/run_remote_heavy.sh` (N=100 reinas, 1000 nodos) y
  `scripts/run_remote_overnight.sh` (exploratorio) corren en background vía `nohup`. Sus
  resultados se traen de vuelta con `rsync` a `results/`, y el mismo notebook los lee igual que
  si se hubieran generado localmente.

### Sobre "encontrar todas las soluciones para N=100"

El número de soluciones de N-reinas crece muy rápido (para N=27 ya son más de $2.34\times10^{17}$,
[OEIS A000170](https://oeis.org/A000170)); una enumeración exhaustiva real para N=100 no es
viable en el tiempo de esta tarea. `enumerate_solutions` (en `src/problems/nqueens.py`) reutiliza
el motor genérico `backtrack` con `find_all=True` (MRV+LCV+forward checking) y corta por
`max_solutions`/`time_limit_seconds` (`configs/nqueens.yaml`), reportando honestamente en
`stats.extra["exhaustive"]` si la búsqueda fue exhaustiva o se cortó.

## Cómo el notebook responde cada pregunta

`notebooks/results.ipynb` tiene un índice al inicio y está organizado **por sección del
enunciado**, en el mismo orden que la tabla de arriba:

- **Sección 1** — qué módulo de `src/csp/` y `src/metaheuristics/` resuelve cada parte de
  implementación (tabla + explicación corta).
- **Sección 2** — N=8 corre en vivo (backtracking + recocido simulado, ambos validados con
  `is_valid_nqueens_solution`); N=100 igual, más una tabla comparativa desde
  `results/tables/nqueens.csv`.
- **Sección 3** — enumeración de todas las soluciones de N=100 (acotada), con la justificación
  de por qué una enumeración exhaustiva no es viable, y referencia a la Sección 7 para el
  experimento exploratorio que profundiza en esto.
- **Sección 4** — coloreado de 50 nodos corre en vivo (incluye el diagnóstico de por qué
  `k_max=12` del config no alcanza, con la tabla de transición de fase); 1000 nodos se lee desde
  los resultados traídos del remoto (`coloring_large_gallop_overnight.txt`, k=302 confirmado por
  OR-Tools, más la comparación backtracking/SA en ese k desde `graph_coloring_k302_overnight.csv`).
- **Sección 5** — comparación completa contra OR-Tools (50 nodos en vivo, 1000 nodos desde el
  remoto), con la tabla y las dos gráficas (`coloring_comparison_k.png`, `_time.png`) y la
  lectura de resultados.
- **Sección 6** — tic-tac-toe con minimax: describe las tres piezas de código, y corre las tres
  validaciones citadas en el reporte (minimax vs. minimax siempre empata; minimax nunca pierde
  contra un agente aleatorio jugando de cualquier lado; el caso a mano que conecta con el
  Ejercicio 3, confirmando `mini_max(env,X)=1` y `best_move(env,X)=2`).
- **Sección 7** (extra, no pedida por el enunciado) — comparación de las tres agendas de
  enfriamiento del recocido simulado, y dos experimentos de "hasta dónde da el cómputo"
  (enumeración de N=100 durante 6 horas sin heurística de orden — 0 soluciones, ilustra
  heavy-tailed runtime; coloreado sin forward checking/AC3 sobre el grafo aleatorio original).
- **Resumen y estado** (última celda) — tabla con el estado de cada parte del enunciado y dónde
  se resuelve; los Ejercicios 1-4 y las críticas de lectura se marcan como resueltos en
  `report/report.tex`/`report.pdf`, ya que por ser papel/matemáticas no producen código que
  vivir en el notebook (excepto el Ejercicio 3, verificado cruzadamente en la Sección 6).

## Compilar el reporte

```bash
cd report && pdflatex -interaction=nonstopmode report.tex && pdflatex -interaction=nonstopmode report.tex
```

(Dos pasadas para resolver referencias cruzadas `\ref`/`\label`. `report/report.pdf` está en
`.gitignore` — se entrega como el PDF pedido por el enunciado, no versionado en git.)
