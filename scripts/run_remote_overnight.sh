#!/usr/bin/env bash
set -euo pipefail

# Corridas exploratorias de "hasta donde aguanta el computo", NO pedidas
# por el enunciado -- separado de scripts/run_remote_heavy.sh (que se
# queda rapido, sin tocar este script).
#
# Orden deliberado: primero compare_schedulers.py (rapido, ~1 min) para
# tener esos resultados asegurados ANTES de comprometer el servidor a las
# ~12 horas combinadas de las otras dos corridas -- si algo falla o se
# corta la sesion despues, al menos ya quedo eso guardado.
#
# Ambas corridas registran, ademas del tiempo, nodes_expanded y memoria
# pico (stats.extra["peak_memory_mb"]) -- ver los prints al final de cada
# una, o results/tables/*_overnight.csv -- para poder evaluar el limite
# real de computo, no solo si terminaron o no.
#
# 1) enumerate_nqueens_overnight.py -- N=100, 6 horas de presupuesto (vs.
#    las 5 min de la version normal, que no encuentra ninguna solucion).
# 2) run_graph_coloring_overnight.py -- coloreado de 1000 nodos, k=8, SIN
#    forward checking ni AC3 (backtracking puro), 6 horas de presupuesto.
#    Contraste directo contra la version con heuristicas, que resuelve el
#    mismo k=8 en ~8.5s (ver results/tables/graph_coloring.csv).
#
# Uso, ya en el servidor remoto:
#
#   nohup bash scripts/run_remote_overnight.sh > logs/run_overnight.log 2>&1 &
#   disown
#   tail -f logs/run_overnight.log
#
# Corre desde la raiz del repo (donde vive este script bajo scripts/).
cd "$(dirname "${BASH_SOURCE[0]}")/.."

mkdir -p logs

echo "[1/3] Comparacion de schedulers (misma semilla de siempre, rapido)"
python experiments/compare_schedulers.py

echo "[2/3] N-reinas N=100: enumerar TODAS las soluciones, presupuesto de 6 horas"
python experiments/enumerate_nqueens_overnight.py

echo "[3/3] Coloreado 1000 nodos, k=8, SIN FC/AC3, presupuesto de 6 horas"
python experiments/run_graph_coloring_overnight.py

echo "Listo. Resultados en results/tables/*_overnight.csv y results/solutions/*_overnight*.json"
echo "Traelos de vuelta a la laptop con, por ejemplo:"
echo '  rsync -avz -e "ssh -p 264" diego@132.248.52.48:~/csp-adversarial-search-hw2/results/ ./results/'
