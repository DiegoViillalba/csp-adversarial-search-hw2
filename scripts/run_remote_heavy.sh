#!/usr/bin/env bash
set -euo pipefail

# Corre los escenarios PESADOS de la Tarea 2 (N-reinas N=100, enumeracion de
# todas las soluciones N=100, coloreado de grafos con 1000 nodos, y la
# comparacion contra OR-Tools) — pensado para el servidor remoto, no la
# laptop local. Los escenarios livianos (N=8 reinas, 50 nodos) se corren
# aparte en notebooks/local_results.ipynb.
#
# tic_tac_toe / minimax / alpha_beta quedan fuera: aun no estan resueltos.
#
# Uso, ya en el servidor remoto (tras "git clone" y "pip install -r
# requirements.txt" dentro de un venv activado):
#
#   nohup bash scripts/run_remote_heavy.sh > logs/run_all.log 2>&1 &
#   disown          # para que sobreviva si se cierra la sesion SSH
#   tail -f logs/run_all.log     # para ver el progreso
#
# Corre desde la raiz del repo (donde vive este script bajo scripts/).
cd "$(dirname "${BASH_SOURCE[0]}")/.."

mkdir -p logs

echo "[1/4] N-reinas (N=8 y N=100, backtracking + metaheuristica)"
python experiments/run_nqueens.py

echo "[2/4] Enumerar todas las soluciones de N-reinas N=100 (acotado)"
python experiments/enumerate_nqueens.py

echo "[3/4] Coloreado de grafos (50 y 1000 nodos, backtracking + metaheuristica)"
python experiments/run_graph_coloring.py

echo "[4/5] Coloreado de grafos vs. OR-Tools (comparacion de tiempo/calidad)"
python experiments/compare_coloring.py

echo "[5/5] Generar graficas para el reporte"
python experiments/make_plots.py

echo "Listo. Resultados en results/tables/ y results/solutions/, graficas en report/figures/."
echo "Traelos de vuelta a la laptop con, por ejemplo:"
echo '  rsync -avz -e "ssh -p 264" diego@132.248.52.48:~/hw2/results/ ./results/'
echo '  rsync -avz -e "ssh -p 264" diego@132.248.52.48:~/hw2/data/graphs/ ./data/graphs/'
echo '  rsync -avz -e "ssh -p 264" diego@132.248.52.48:~/hw2/report/figures/ ./report/figures/'
